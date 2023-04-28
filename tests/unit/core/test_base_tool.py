import inspect
import os
import pytest
import yaml
from schema import SchemaMissingKeyError

from griptape.drivers import MemoryStorageDriver
from griptape.middleware import StorageMiddleware
from tests.mocks.mock_tool.tool import MockTool


class TestBaseTool:
    @pytest.fixture
    def tool(self):
        return MockTool(
            test_field="hello",
            test_int=5
        )

    def test_env_fields(self, tool):
        assert len(tool.env_fields) == 2

    def test_env(self, tool):
        assert tool.env["TEST_FIELD"] == "hello"

    def test_manifest_path(self, tool):
        assert tool.manifest_path == os.path.join(tool.abs_dir_path, tool.MANIFEST_FILE)

    def test_dockerfile_path(self, tool):
        assert tool.dockerfile_path == os.path.join(tool.abs_dir_path, tool.DOCKERFILE_FILE)

    def test_requirements_path(self, tool):
        assert tool.requirements_path == os.path.join(tool.abs_dir_path, tool.REQUIREMENTS_FILE)

    def test_manifest(self, tool):
        with open(tool.manifest_path, "r") as yaml_file:
            assert tool.manifest == yaml.safe_load(yaml_file)

    # TODO: add test for default dockerfile
    def test_dockerfile(self, tool):
        with open(tool.dockerfile_path, "r") as dockerfile:
            assert tool.dockerfile == yaml.safe_load(dockerfile)

    def test_abs_file_path(self, tool):
        assert tool.abs_file_path == os.path.abspath(inspect.getfile(tool.__class__))

    def test_abs_dir_path(self, tool):
        assert tool.abs_dir_path == os.path.dirname(tool.abs_file_path)

    def test_env_value(self, tool):
        assert tool.env_value("TEST_FIELD") == "hello"
        assert tool.env_value("TEST_INT") == 5
        assert tool.env_value("NO_TEST_FIELD") is None

        os.environ["TEST_INT"] = "1"

        assert isinstance(tool.env_value("TEST_INT"), int)
        assert tool.env_value("TEST_INT") == 1

    def test_activity_name(self, tool):
        assert tool.activity_name(tool.test) == "test"

    def test_name(self):
        assert MockTool().name == "MockTool"
        assert MockTool(name="FooBar").name == "FooBar"

    def test_class_name(self):
        assert MockTool().class_name == "MockTool"
        assert MockTool(name="FooBar").class_name == "MockTool"

    def test_activity_description(self, tool):
        description = tool.activity_description(tool.test)

        assert "bar" in description
        assert "baz" not in description

    def test_full_action_description(self, tool):
        description = tool.full_activity_description(tool.test)

        assert "bar" in description
        assert "baz" not in description

    def test_activity_schema(self, tool):
        assert tool.activity_schema(tool.test) == \
               tool.test.config["schema"].json_schema("ToolInputSchema")

    def test_find_action(self, tool):
        assert tool.find_activity("test") == tool.test

    def test_activities(self, tool):
        assert len(tool.activities()) == 1
        assert tool.activities()[0] == tool.test

    def test_validate(self, tool):
        assert tool.validate()

    def test_invalid_config(self):
        try:
            from tests.mocks.invalid_mock_tool.tool import InvalidMockTool
        except SchemaMissingKeyError as e:
            assert True

    def test_custom_config(self, tool):
        assert tool.test.config["foo"] == "bar"

    def test_middleware(self):
        tool = MockTool(
            middleware={
                "test": [
                    StorageMiddleware(
                        name="Middleware1", driver=MemoryStorageDriver()
                    ),
                    StorageMiddleware(
                        name="Middleware2", driver=MemoryStorageDriver()
                    )
                ]
            },
            test_field="hello",
            test_int=5
        )

        assert len(tool.middleware["test"]) == 2

    def test_middleware_validation(self):
        try:
            MockTool(
                middleware={
                    "test": [
                        StorageMiddleware(
                            name="Middleware1", driver=MemoryStorageDriver()
                        ),
                        StorageMiddleware(
                            name="Middleware1", driver=MemoryStorageDriver()
                        )
                    ]
                },
                test_field="hello",
                test_int=5
            )
        except ValueError:
            assert True