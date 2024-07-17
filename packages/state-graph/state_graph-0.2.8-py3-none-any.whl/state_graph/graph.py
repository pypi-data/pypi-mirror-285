from rich import print
import os
import ipdb
import traceback
import uuid
import json
from typing import TypedDict, Any, get_type_hints, Annotated, get_origin
import operator
from pydantic import BaseModel, create_model
from typing import Any
from typing import (
    Awaitable,
    Callable,
    Literal,
    get_args,
    TypeVar,
    Any,
    Annotated,
)
import asyncio
import networkx as nx
from IPython.display import display, HTML, Javascript, Image
import time
import base64
from . import utils
from .node import Node, EndNode, WaitingNode, StartNode
from .edge import Edge, SimpleEdge


# beartype_this_package()


T = TypeVar("T", bound=BaseModel)


class NodeDefinition(BaseModel):
    name: str
    label: str | None = None


class EdgeDefinition(BaseModel):
    name: str
    label: str | None = None
    start_node: str
    out_nodes: list[str]


class GraphDefinition(BaseModel):
    nodes: list[NodeDefinition]
    edges: list[EdgeDefinition]


class Event(BaseModel):
    run_id: str
    context: BaseModel
    output: dict | None
    start_time: float
    end_time: float
    duration: float
    name: str
    event_type: Literal[
        "node_execution_error", "edge_execution_error", "state_enter", "state_exit"
    ]
    message: str | None = None
    logs: str | None = None
    t: int


class NodeState:
    def __init__(
        self,
        node: Node,
        context: BaseModel,
        partial_context: BaseModel | dict,
        is_waiting: bool = False,
        is_done: bool = False,
    ):
        self.node = node
        self.context = context
        self.partial_context = partial_context
        self.is_waiting = is_waiting
        self.is_done = is_done

    @property
    def name(self):
        return self.node.name

    @property
    def merge_flows(self):
        return self.node.merge_flows


def create_subset_model(parent: BaseModel, props: list[str]) -> BaseModel:
    field_definitions = {}
    for prop in props:
        if prop in parent.model_fields:
            field = parent.model_fields[prop]
            annotation = field.annotation
            # If the annotation is a GenericAlias (like list[str]), use Any instead
            if hasattr(annotation, "__origin__"):
                annotation = Any
            field_definitions[prop] = (annotation, ...)
        elif hasattr(parent, prop):
            # If the property exists but is not in model_fields, add it as Any
            field_definitions[prop] = (Any, ...)

    SubsetModel = create_model(
        "SubsetModel",
        **field_definitions,
        __base__=BaseModel,
    )

    # Create an instance of the SubsetModel with values from the parent
    subset_data = {}
    for prop in props:
        if hasattr(parent, prop):
            value = getattr(parent, prop)
            # If the value is a GenericAlias, convert it to a regular list
            if hasattr(type(value), "__origin__") and type(value).__origin__ is list:
                value = list(value)
            subset_data[prop] = value

    # Create and return the instance
    return SubsetModel(**subset_data)


class Graph:
    """
    A graph represents the workflow of the app. It has a dynamic context that can be changed by the nodes and an optional
    static context that is not changed by the nodes.
    """

    nodes: dict[str, Node]
    edges: dict[str, Edge]
    graph: nx.MultiDiGraph
    current_node: Node
    context: BaseModel
    __initial_context: BaseModel
    __on_state_enter_callbacks: dict[str, Callable[[BaseModel], Awaitable] | None]
    __on_state_exit_callbacks: dict[str, Callable[[BaseModel], Awaitable] | None]
    guards: list[Callable[[BaseModel], str | None]] = []
    on_event: Callable[[Event], Awaitable] | None = None
    run_id: str

    @property
    def stream_token(self):
        return self.__stream_token

    @stream_token.setter
    def stream_token(self, value: Callable[[str], Awaitable]):
        self.__stream_token = value
        for node in self.nodes.values():
            node._set_stream_token(value)

    def restore_state(self, state: dict[str, Any]):
        self.context = utils.merge_context(self.context, state)

    def compile(self) -> None:
        """
        Check that the graph looks right.
        Using the already built MultiDiGraph object, check the following:
            - node start has exactly one edge going out
            - node end has exactly zero edges going in
            - the end node, if present, has zero edges going out
            - no node has zero edges going in, except for the start node.
            - check that the nodes that each edge points to exist
            - check that the nodes that each edge comes from exist
            - check that all nodes, except for the end node, have at least one edge goin out
        Raises an exception if any of these conditions are not met.
        """
        start_node_out_edges = self.graph.out_edges("start")
        if len(start_node_out_edges) != 1:
            raise ValueError(
                f"'start' node must have exactly one edge going out, found {len(start_node_out_edges)}"
            )
        end_node_out_edges = self.graph.out_edges("end")
        if len(end_node_out_edges) != 0:
            raise ValueError(
                f"'end' node must have zero edges going out, found {len(end_node_out_edges)}"
            )

        for node in self.graph.nodes:
            if node != "start" and self.graph.in_degree(node) == 0:
                raise ValueError(
                    f"Node '{node}' has zero edges going in, which is not allowed except for the start node."
                )

        for edge in self.edges.values():
            target_nodes = edge.out_nodes
            for target_node in target_nodes:
                if target_node not in self.nodes:
                    raise ValueError(
                        f"Edge '{edge.name}' points to non-existent node '{target_node}'"
                    )
            if edge.start_node not in self.nodes:
                raise ValueError(
                    f"Edge '{edge.name}' points to non-existent node '{edge.start_node}'"
                )

        for node in self.nodes.values():
            if node.name != "end" and self.graph.out_degree(node.name) == 0:
                raise ValueError(
                    f"Node '{node.name}' has zero edges going out, which is not allowed except for the end node."
                )

        self.__is_compiled = True

    def reset(
        self, new_state: dict[str, Any] | None = None, id: str | None = None
    ) -> "Graph":
        new_state = new_state or {}
        dump = self.__initial_context.model_copy().model_dump() | new_state
        initial_context = self.__initial_context.__class__(**dump)
        new_graph = Graph(
            context=initial_context,
            name=self.graph.name,
            nodes=self.nodes.copy(),
            edges=self.edges.copy(),
            stream_token=self.__stream_token,
            _is_compiled=self.__is_compiled,
            id=id,
            guards=self.guards,
            on_event=self.on_event,
        )
        return new_graph

    __stream_token: Callable[[str], Awaitable]

    def __init__(
        self,
        *,
        context: BaseModel,
        name: str = "graph",
        nodes: dict[str, Node] | None = None,
        edges: dict[str, Edge] | None = None,
        stream_token: Callable[[str], Awaitable] | None = None,
        on_state_enter: (
            dict[str, Callable[[BaseModel], Awaitable] | None] | None
        ) = None,
        on_state_exit: dict[str, Callable[[BaseModel], Awaitable] | None] | None = None,
        _is_compiled: bool = False,
        id: str | None = None,
        guards: list[Callable[[BaseModel], str | None]] | None = None,
        on_event: Callable[[Event], Awaitable] | None = None,
    ) -> None:
        nodes = nodes if nodes is not None else {}
        edges = edges if edges is not None else {}
        self.nodes = {}
        self.edges = {}
        self.guards = guards if guards is not None else []
        self.name = name
        self.graph = nx.MultiDiGraph(name=name)
        self.__initial_context = context
        self.context = context.copy()
        self.__is_compiled = _is_compiled
        self.run_id = id or str(uuid.uuid4())
        self.t: int = 0
        self.on_event = on_event

        async def _stream_token(token: str):
            pass

        self.__stream_token = (
            stream_token if stream_token is not None else _stream_token
        )
        if "start" not in nodes:
            # self.add_node(StartNode())
            self.nodes["start"] = StartNode()

        for node in nodes.values():
            self.add_node(node)

        for edge in edges.values():
            self.add_edge(edge)

        self.current_node = self.nodes["start"]

        self.__on_state_enter_callbacks = (
            on_state_enter if on_state_enter is not None else {}
        )
        self.__on_state_exit_callbacks = (
            on_state_exit if on_state_exit is not None else {}
        )

    def on_state_enter(self, state: str, callback: Callable):
        assert state in self.nodes, f"Node {state} does not exist."
        self.__on_state_enter_callbacks[state] = callback

    def on_state_exit(self, state: str, callback: Callable):
        assert state in self.nodes, f"Node {state} does not exist."
        self.__on_state_exit_callbacks[state] = callback

    def add_node(self, node: Node):
        assert node.name not in self.nodes, f"Node {node.name} already exists"
        self.nodes[node.name] = node
        self.graph.add_node(node.name, color=node.color)
        node._set_stream_token(self.__stream_token)

    def add_edge(self, edge: Edge):
        assert edge.name not in self.edges, f"Edge {edge.name} already exists"
        assert (
            edge.start_node in self.nodes
        ), f"Edge {edge.name} points to non-existent node {edge.start_node}"
        assert all(
            out_node in self.nodes for out_node in edge.out_nodes
        ), f"Edge {edge.name} points to non-existent node(s)"
        self.edges[edge.name] = edge
        for out_node in edge.out_nodes:
            self.graph.add_edge(
                edge.start_node, out_node, label=edge.name, directed=True
            )

    def add_simple_edge(
        self,
        start_node: str | Node,
        out_node: str | Node,
        name: str | None = None,
        label: str | None = None,
    ):
        self.add_edge(SimpleEdge(start_node, out_node, name, label))

    def __log_event(self, event: Event):
        if event.name == "start" and event.t > 0:
            ipdb.set_trace()
        assert not (
            event.name == "start" and event.t > 0
        ), "Start node cannot have t > 0"
        if self.on_event is not None:
            on_event = self.on_event(event)
            asyncio.create_task(on_event)

    def guard(self, context: BaseModel, message: str):
        for guard in self.guards:
            result = guard(context)
            if result is not None:
                print(context)
                assert False, f"Guard {guard}\nfailed: {message}\nError Cause: {result}"

    async def run(self, input: dict[str, Any] | None = None) -> tuple[BaseModel, bool]:
        assert self.__is_compiled, "Graph must be compiled before running"
        input = input or {}

        if self.current_node.name == "start":
            assert self.t == 0, "Graph must be reset before running"

        self.context = utils.merge_context(self.context, input)
        active_nodes = await self.run_node(
            NodeState(self.current_node, self.context, self.context)
        )

        self.t += 1

        while active_nodes:
            new_active_nodes: list[NodeState] = []
            tasks = []
            task_names = []

            for node_state in active_nodes:
                if node_state.is_done or node_state.is_waiting:
                    new_active_nodes.append(node_state)
                elif len(active_nodes) > 1 and node_state.merge_flows:
                    new_active_nodes.append(node_state)
                else:
                    tasks.append(self.run_node(node_state))
                    task_names.append(node_state.node.name)

            if tasks:
                print(
                    f"[blue] [{self.t}] [/blue] [yellow] RUNNING {len(tasks)} TASKS [/yellow]"
                )
                results = await asyncio.gather(*tasks)
                for result in results:
                    new_active_nodes.extend(result)

            active_nodes = new_active_nodes

            if len(active_nodes) == 1:
                print(f"{active_nodes[0].node.name=}")
                self.context = active_nodes[0].context
                self.current_node = active_nodes[0].node

            # Check if all nodes have stopped (waiting or done)
            if all(
                node.is_done or node.merge_flows or node.is_waiting
                for node in active_nodes
            ):
                node_names = set(node.node.name for node in active_nodes)
                # Verify that all stopped nodes are in the same state
                if len(node_names) > 1:
                    raise ValueError(
                        f"Nodes have stopped in different states: {node_names}"
                    )

                partial_contexts = [
                    (
                        node.partial_context
                        if isinstance(node.partial_context, dict)
                        else node.partial_context.model_dump()
                    )
                    for node in active_nodes
                ]
                all_keys = []
                for partial_context in partial_contexts:
                    all_keys.extend(partial_context.keys())

                assert len(set(all_keys)) == len(all_keys), "All keys must be unique"

                merged_context_dict = {}
                for partial_context in partial_contexts:
                    merged_context_dict.update(partial_context)
                for key in merged_context_dict:
                    assert hasattr(self.context, key), f"Context has no attribute {key}"
                merged_context = self.context.model_copy()
                for key, value in merged_context_dict.items():
                    setattr(merged_context, key, value)
                self.guard(
                    merged_context, f"Guards failed after merging nodes {node_names}"
                )
                is_done = all(node.is_done for node in active_nodes)
                is_waiting = all(node.is_waiting for node in active_nodes)
                if is_waiting or is_done:
                    self.t += 1
                    return merged_context, is_done
                else:
                    # print(merged_context)
                    active_nodes = [
                        NodeState(active_nodes[0].node, merged_context, merged_context)
                    ]

            print(
                f"New active nodes names: {[node.node.name for node in active_nodes]}"
            )
            self.t += 1
        return self.context, True  # this will hopefully never happen.

    async def run_node(self, node_state: NodeState) -> list[NodeState]:
        node = node_state.node
        context = node_state.context

        self.guard(context, f"Guard failed before node {node.name}")

        if node.name in self.__on_state_enter_callbacks:
            callback = self.__on_state_enter_callbacks[node.name]
            if callback is not None:
                await callback(context)

        subset_context = create_subset_model(context, node.input_fields)
        start_time = time.time()
        end_time = -1
        duration = -1
        try:
            print(
                f"[blue] [{self.t}] [/blue] [orange] RUNNING NODE [/orange] {node.name}"
            )
            context_update, logs = await node.run_with_logs(subset_context, self.run_id)
            end_time = time.time()
            duration = end_time - start_time
            print(
                f"[blue] [{self.t}] [/blue] [green] FINISHED NODE [/green] {node.name}"
            )
        except Exception as e:
            error_msg: str = str(e)
            traceback_details: str = traceback.format_exc()
            event = Event(
                output=None,
                context=subset_context,
                event_type="node_execution_error",
                name=node.name,
                run_id=self.run_id,
                message=f"{error_msg}\nTraceback: {traceback_details}",
                logs="\n".join(node._logs),
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                t=self.t,
            )
            if self.on_event is not None:
                await self.on_event(event)
            print(f"[red]ERRRRRRRROOOOOOOOOR")
            await asyncio.sleep(1)
            raise e

        new_context = utils.update_context(context, context_update)
        self.guard(new_context, f"Guard failed after node {node.name}")
        self.__log_event(
            Event(
                output=(
                    context_update
                    if isinstance(context_update, dict)
                    else context_update.model_dump()
                ),
                context=subset_context,
                event_type="state_exit",
                name=node.name,
                run_id=self.run_id,
                logs="\n".join(logs),
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                t=self.t,
            )
        )
        if node.name in self.__on_state_exit_callbacks:
            callback = self.__on_state_exit_callbacks[node.name]
            if callback is not None:
                await callback(new_context)

        next_nodes = self.get_next_nodes(node.name, new_context, self.t)
        next_nodes_names = [n.name for n in next_nodes]

        # if set(next_nodes_names) == {"decide_to_run_tool", "analyze_query"}:
        #     ipdb.set_trace()

        assert (
            not "start" in next_nodes_names
        ), f"Node {node.name} has a next node named 'start'"

        if len(next_nodes) > 1:
            assert (
                node.allow_flow_split
            ), f"Node {node.name} has multiple outgoing edges but is not set to allow flow split"
        else:
            assert (
                not node.allow_flow_split
            ), f"Node {node.name} has only one outgoing edge but is set to allow flow split"

        print(f"{next_nodes_names=}")
        return [
            NodeState(
                next_node,
                new_context,
                context_update,
                is_waiting=isinstance(next_node, WaitingNode),
                is_done=isinstance(next_node, EndNode),
            )
            for next_node in next_nodes
        ]

    def get_next_nodes(
        self, current_node_name: str, context: BaseModel, t: int
    ) -> list[Node]:
        matching_edges = [
            e for e in self.edges.values() if e.start_node == current_node_name
        ]
        assert len(matching_edges) != 0, f"No edges found for node {current_node_name}"

        next_nodes = []
        for edge in matching_edges:
            start_time = time.time()
            end_time = -1
            duration = -1
            try:
                next_node_names = edge.fn(context)
                end_time = time.time()
                duration = end_time - start_time
                if isinstance(next_node_names, str):
                    next_node_names = [next_node_names]
                for next_node_name in next_node_names:
                    assert (
                        next_node_name in edge.out_nodes
                    ), f"Edge {edge.name} does not have a valid out node {next_node_name}"
                    next_nodes.append(self.nodes[next_node_name])
                print(
                    f"[red]Node {current_node_name}[/red] -> [yellow]Edge {edge.name} [/yellow] -> {next_node_names}"
                )
            except Exception as e:
                self.__log_event(
                    Event(
                        output=None,
                        context=context,
                        event_type="edge_execution_error",
                        name=edge.name,
                        run_id=self.run_id,
                        message=str(e),
                        t=t,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                    )
                )
                raise e

        return next_nodes

    def get_definition(self) -> GraphDefinition:
        assert (
            self.__is_compiled
        ), "Graph must be compiled before getting the definition"
        return GraphDefinition(
            nodes=[NodeDefinition(name=k) for k in self.nodes.keys()],
            edges=[
                EdgeDefinition(
                    start_node=v.start_node, out_nodes=list(v.out_nodes), name=v.name
                )
                for k, v in self.edges.items()
            ],
        )

    def plot(self, destination: str | None = None):
        print("plotting")
        assert self.__is_compiled, "Graph must be compiled before plotting"
        # Start of the Mermaid.js diagram
        mermaid_diagram = f"""
---        
title: {self.name}
---
stateDiagram-v2
"""
        # Unique color tracking for class definition
        color_classes = {}
        class_counter = 1

        # Collect all unique colors and define class styles
        for node in self.nodes.values():
            if hasattr(node, "color") and node.color not in color_classes:
                class_name = f"class{class_counter}"
                color_classes[node.color] = class_name
                mermaid_diagram += (
                    f"    classDef {class_name} fill:{node.color}, stroke:#333\n"
                )
                class_counter += 1

        # Adding all transitions
        for edge in self.edges.values():
            for i, out_node in enumerate(edge.out_nodes):
                transition = (
                    f"    {edge.start_node} --> {out_node} : {edge.labels[i]}\n"
                )
                mermaid_diagram += transition

        # Assigning classes to nodes based on their colors
        for node_name, node in self.nodes.items():
            if hasattr(node, "color"):
                mermaid_diagram += (
                    f"    class {node_name} {color_classes[node.color]}\n"
                )

        def get_img_url(graph) -> str:
            graphbytes = graph.encode("ascii")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")
            return "https://mermaid.ink/img/" + base64_string

        img_url = get_img_url(mermaid_diagram)
        if destination is not None:
            utils.save_mermaid_to_html(
                mermaid_diagram, os.path.join(destination, "graph.html")
            )
        else:
            print("here")
            # get_img_url(mermaid_diagram)
            display(Image(url=img_url))
        #     display(HTML(out_html))
        #     # show_mermaid(mermaid_diagram)
