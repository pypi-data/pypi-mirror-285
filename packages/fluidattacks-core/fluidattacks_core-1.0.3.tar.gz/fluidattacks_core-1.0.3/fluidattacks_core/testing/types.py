# pylint: disable=invalid-name
from mypy_boto3_dynamodb.service_resource import (
    DynamoDBServiceResource,
    Table,
)
from mypy_boto3_dynamodbstreams.client import (
    DynamoDBStreamsClient,
)
from typing import (
    Callable,
    Generator,
    Literal,
    NamedTuple,
    TypeAlias,
    TypedDict,
    TypeVar,
)
from unittest.mock import (
    _patch,
)

T = TypeVar("T")

DynamoDBTable: TypeAlias = Table
DynamoDBResource: TypeAlias = DynamoDBServiceResource
DynamoStreamsClient: TypeAlias = DynamoDBStreamsClient
Patch: TypeAlias = _patch

SetupFixture: TypeAlias = None
FunctionFixture: TypeAlias = Callable[..., T]
GeneratorFixture: TypeAlias = Generator[T, None, None]

EventType = Literal["INSERT", "MODIFY", "REMOVE"]
RecordType = Literal[
    "NEW_IMAGE", "OLD_IMAGE", "NEW_AND_OLD_IMAGES", "KEYS_ONLY"
]
VulnerabilityStatusType = Literal[
    "SAFE", "VULNERABLE", "SUBMITTED", "REJECTED"
]
TreatmentStatusType = Literal[
    "UNTREATED", "IN_PROGRESS", "ACCEPTED", "ACCEPTED_UNDEFINED"
]
SeverityLevelType = Literal["low", "medium", "high", "critical"]


class AttributeValue(TypedDict, total=False):
    S: str
    N: str
    B: bytes
    SS: list[str]
    NS: list[str]
    BS: list[bytes]
    M: dict[str, "AttributeValue"]
    L: list["AttributeValue"]
    NULL: bool
    BOOL: bool


class MockedInstance:
    """
    Wrapper for general purpose instance mocking.

    When you need to mock elements with properties accessed via dot notation,
    you can use this class to mock the instance and override behaviors.
    """

    def __init__(self, **attrs: int | str | bool | dict | list) -> None:
        self.__dict__.update(**attrs)

    def __getattr__(self, attr: str) -> str | None:
        return self.__dict__.get(attr, None)

    def __enter__(self) -> "MockedInstance":
        return self

    def __exit__(self, *args: tuple, **kwargs: dict) -> None:
        # __exit__ should exist for context manager handling
        pass

    async def __aenter__(
        self, *args: tuple, **kwargs: dict
    ) -> "MockedInstance":
        return self

    async def __aexit__(self, *args: tuple, **kwargs: dict) -> None:
        # __aexit__ should exist for context manager handling
        pass


class FunctionCall(NamedTuple):
    """Function call tuple item. It stores args, kwargs and result."""

    args: tuple
    kwargs: dict
    result: object


class FunctionCallsStore:
    """Class with some methods for storing function calls."""

    calls_store: list[FunctionCall] = []

    def __init__(self) -> None:
        self.reset()

    def append_call(self, args: tuple, kwargs: dict, result: object) -> None:
        """Appends a new function call to the store"""
        self.calls_store.append(
            FunctionCall(args=args, kwargs=kwargs, result=result)
        )

    def calls(self) -> list[FunctionCall]:
        """Returns stored function calls."""
        return self.calls_store

    def reset(self) -> None:
        """Resets the store."""
        self.calls_store = []


MockingFunction: TypeAlias = FunctionFixture[FunctionCallsStore]
