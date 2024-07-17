from typing import Literal

from pydantic import BaseModel
from typing import Literal, Annotated
import operator
import asyncio

from . import utils
from .graph import Graph
from .node import Node, WaitingNode
from .edge import edge, SimpleEdge


async def main():

    async def stream_token(token: str):
        print(token)

    class Context(BaseModel):
        chat: Annotated[list[dict[str, str]], operator.add]

    class Node1(Node):
        async def run(self, context: Context) -> dict | BaseModel:

            # gets the last user message (if any)
            last_user_message = next(
                (
                    message
                    for message in reversed(context.chat)
                    if message["role"] == "user"
                ),
                None,
            )
            if last_user_message is not None:
                print(f"Last user message: {last_user_message['content']}")
            context.chat.append(
                dict(
                    role="assistant",
                    content=f"Hello, {last_user_message['content'] if last_user_message else ''}",
                )
            )
            await self.stream_token(context.chat[-1]["content"])
            return context

    node1 = Node1(name="node1")
    node2 = WaitingNode(name="node2")

    # Create edges
    @edge("node1")
    def edge1(context: dict) -> Literal["node2"]:
        return "node2"

    @edge("node2")
    def edge2(context: dict) -> Literal["node1"]:
        return "node1"

    # Create a graph
    graph = Graph(stream_token=stream_token, context=Context(chat=[]))
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge(SimpleEdge("start", "node1"))
    graph.add_edge(edge1)
    graph.add_edge(edge2)

    print(graph.graph)
    # Plot the graph
    # graph.plot()

    # Run the graph
    is_end = False
    while not is_end:
        # If the execution is not ended, it means a waiting node is encountered
        some_input = input(f"Enter input for node {graph.current_node.name}: ")
        _, is_end = await graph.run(
            input=dict(chat=[dict(role="user", content=some_input)])
        )


if __name__ == "__main__":
    asyncio.run(main())
