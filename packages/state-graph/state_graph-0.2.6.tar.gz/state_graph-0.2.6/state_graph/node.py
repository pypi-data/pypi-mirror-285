from re import I
from regex import P
from rich import print
import os
from typing import TypedDict, Any, get_type_hints, Annotated, get_origin
import operator
from pydantic import BaseModel
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
import base64
from . import utils


T = TypeVar("T", bound=BaseModel)


class Node(BaseModel):
    """
    A node is a state in the state graph. Basically it's a function that can mutate the state.
    """

    name: str
    color: str = "blue"
    static_context: BaseModel | None = None
    input_fields: list[str] = []
    merge_flows: bool = False
    allow_flow_split: bool = False
    _stream_token: list[Callable[[str], Awaitable]] = []
    _logs: list[str] = []

    class Config:
        frozen = True

    @property
    def stream_token(self):
        assert len(self._stream_token) == 1, "stream_token must be set."
        return self._stream_token[0]

    def _set_stream_token(self, value: Callable[[str], Awaitable]):
        if len(self._stream_token) > 0:
            # replace it
            self._stream_token[0] = value
        else:
            self._stream_token.append(value)

    async def run(self, context: T) -> dict | T:
        return {}

    async def run_with_logs(self, context: T) -> tuple[dict | T, list[str]]:
        self._logs = []
        return await self.run(context), self._logs

    def log(self, message: Any, print_also=True):
        self._logs.append(message.__repr__())
        if print_also:
            print(message)

    def __init__(
        self,
        static_context: BaseModel | None = None,
        merge_flows: bool = False,
        **kwargs,
    ):
        super().__init__(
            **kwargs, static_context=static_context, merge_flows=merge_flows
        )
        self._logs = []
        if merge_flows:
            print(f"[red]{self.name=} {merge_flows=} [/red]")
        if static_context is not None:
            # check that it is frozen
            assert not utils.is_mutable(
                static_context.__class__
            ), "Static context must be frozen"


class WaitingNode(Node):
    """
    A node that causes the `run` method to finish. The context however is saved. So the next time the graph is run, the context is restored.
    """

    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(name=name, color="orange", input_fields=[], _is_waiting=True)


class StartNode(Node):
    """
    The start node is the first node in the graph. It has no incoming edges.
    """

    def __init__(self) -> None:
        super().__init__(name="start", color="green", input_fields=[])


class EndNode(Node):
    """
    The end node is the last node in the graph. It has no outgoing edges.
    This node is optional.
    """

    def __init__(self, name="end") -> None:
        super().__init__(name=name, color="red", input_fields=[])


def node(
    input_fields: list[str], merge_flows: bool = False, allow_flow_split: bool = False
):
    """
    Decorator to turn a function into a node. This works well for relatively simple nodes.
    """

    def decorator(fn: Callable):
        class _Node(Node):
            def __init__(
                self,
                name: str,
                input_fields: list[str],
            ) -> None:
                super().__init__(
                    name=name,
                    input_fields=input_fields,
                    merge_flows=merge_flows,
                    allow_flow_split=allow_flow_split,
                )

            async def run(self, context: dict) -> dict:
                res = await fn(context)
                return res

        return _Node(name=fn.__name__, input_fields=input_fields)

    return decorator
