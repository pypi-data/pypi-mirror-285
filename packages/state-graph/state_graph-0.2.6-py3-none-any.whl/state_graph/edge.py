from typing import Callable
from pydantic import BaseModel
from typing import Annotated, get_args, get_origin
from .node import Node


class Edge(BaseModel):
    """
    Edges represent transitions between nodes. They can be conditional or unconditional.
    Conditional edges are functions that determine the next state based on the current state and the context.
    """

    fn: Callable
    out_nodes: tuple[str, ...]
    labels: tuple[str, ...]
    name: str
    start_node: str

    def __call__(self, context: dict) -> str:
        return self.fn(context)

    class Config:
        frozen = True


class SimpleEdge(Edge):
    def __init__(
        self,
        start_node: str | Node,
        out_node: str | Node,
        name: str | None = None,
        label: str | None = None,
    ) -> None:
        """
        Creates an unconditional edge from the start node to the out node.
        """
        out_node = out_node.name if isinstance(out_node, Node) else out_node
        start_node = start_node.name if isinstance(start_node, Node) else start_node

        def _fn(_: dict) -> str:
            return out_node

        name = name if name else f"{start_node}->{out_node}"
        label = label if label else ""
        super().__init__(
            fn=_fn,
            out_nodes=(out_node,),
            name=name,
            start_node=start_node,
            labels=(label,),
        )


def edge(start_node: str | Node):
    """
    Decorator to turn a function into a conditional edge.
    The function must have the return type annotated with Literal that determines the possible out nodes.
    Example:
    ```python
    @edge("some_state")
    def should_transtion(context: dict) -> Literal["some_state", "other_state"]:
        if context["some_condition"] == "some_value":
            return "some_state"
        else:
            return "other_state"
    ```
    """
    start_node = start_node.name if isinstance(start_node, Node) else start_node

    def decorator(fn: Callable) -> Edge:
        return_type = fn.__annotations__.get("return")
        assert (
            return_type is not None
        ), f"Function {fn.__name__} must have a return type annotation"
        out_nodes = (
            get_args(return_type)
            if not get_origin(return_type) == Annotated
            else get_args(get_args(return_type)[0])
        )
        # checks if the return type has metadata
        if hasattr(return_type, "__metadata__") and return_type.__metadata__:
            if len(return_type.__metadata__) != len(out_nodes):
                raise ValueError(
                    f"""If you annotate the return type of an edge, the function must return the same number of nodes as the return type annotation.
found len({return_type.__metadata__})=={len(return_type.__metadata__)} != len({out_nodes})=={len(out_nodes)}
"""
                )
            labels = return_type.__metadata__
        else:
            labels = tuple(f"{start_node}->{node}" for node in out_nodes)
        assert all(
            isinstance(node, str) for node in out_nodes
        ), f"All literal values in the return type annotation of function {fn.__name__} must be strings"
        name = fn.__name__
        return Edge(
            fn=fn, out_nodes=out_nodes, name=name, start_node=start_node, labels=labels
        )

    return decorator
