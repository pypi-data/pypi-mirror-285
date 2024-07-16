from .fakers import (
    initialize_db,
)
from .types import (
    DynamoDBResource,
    FunctionCallsStore,
    FunctionFixture,
    GeneratorFixture,
    MockingFunction,
    Patch,
    SetupFixture,
)
import boto3 as _boto3
import moto as _moto
import os as _os
import pytest as _pytest
from unittest.mock import (
    patch,
)


class CustomFixturesPlugin:
    @_pytest.fixture(autouse=True)
    def aws_credentials(self) -> SetupFixture:
        """Mocked AWS Credentials for moto."""
        _os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        _os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        _os.environ["AWS_SECURITY_TOKEN"] = "testing"
        _os.environ["AWS_SESSION_TOKEN"] = "testing"
        _os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    @_pytest.fixture(scope="function")
    def dynamodb_resource(self) -> GeneratorFixture[DynamoDBResource]:
        """Returns a DynamoDB service resource with example table
        for testing purposes.
        """

        with _moto.mock_aws():
            resource = _boto3.resource("dynamodb")
            initialize_db(resource)
            yield resource

    @_pytest.fixture(scope="function")
    def patch_table(
        self, dynamodb_resource: DynamoDBResource
    ) -> FunctionFixture[Patch]:
        """Change a DynamoDB table resource variable with a
        mocked table resource.
        """

        def _mock_table(
            module: object, resource: str, table_name: str
        ) -> Patch:
            table = dynamodb_resource.Table(table_name)
            return patch.object(module, resource, table)

        return _mock_table

    @_pytest.fixture(scope="function")
    def mocking(self, monkeypatch: _pytest.MonkeyPatch) -> MockingFunction:
        store = FunctionCallsStore()

        def _mock(
            module: object, method: str, result: object
        ) -> FunctionCallsStore:
            def _mocked(*args: tuple, **kwargs: dict) -> object:
                store.append_call(args, kwargs, result)
                return result

            monkeypatch.setattr(module, method, _mocked)
            return store

        return _mock
