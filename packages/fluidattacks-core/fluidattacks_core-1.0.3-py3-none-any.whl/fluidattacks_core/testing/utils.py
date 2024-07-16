from .types import (
    AttributeValue,
)
from decimal import (
    Decimal,
)


def _cast_primitive(
    value: str | bool | int | float | Decimal,
) -> AttributeValue:
    if isinstance(value, (str)):
        return {"S": str(value)}
    if isinstance(value, (bool)):
        return {"BOOL": value}
    return {"N": str(value)}


def _cast_objects(value: list | dict) -> AttributeValue:
    if isinstance(value, list):
        return {"L": [cast_to_dynamodb(v) for v in value]}
    return {"M": {key: cast_to_dynamodb(val) for key, val in value.items()}}


def cast_to_dynamodb(
    value: str | bool | int | float | dict | Decimal | None,
) -> AttributeValue:
    """Format vulnerabilities to DynamoDB structure.

    Returns:
        AttributeValue: Vulnerability formatted to DynamoDB types.
    """
    if isinstance(value, (str, bool, int, float, Decimal)):
        return _cast_primitive(value)
    if isinstance(value, (dict, list)):
        return _cast_objects(value)
    return {"NULL": True}
