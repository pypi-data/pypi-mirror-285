from pydantic import BaseModel
from typedllm.tool import Tool, create_tool_from_function


def test_basic_tool_creation(ClassTool):
    result = ClassTool.openapi_json()

    assert result == {
        "type": "function",
        "function": {
            "name": "TestTool",
            "description": "Tool called TestTool",
            "parameters": {
                "type": "object",
                "title": "TestTool",
                "description": "Tool called TestTool",
                "properties": {
                    "value": {
                        "title": "Value",
                        "type": "integer"
                    }
                },
                "required": ["value"]
            }
        }
    }


def test_func_versus_class_tool_creation(FuncTool, ClassTool):
    """
    This test should show that you can create a tool from a function or class and they are equivalent.
    """
    f = FuncTool.openapi_json()
    c = ClassTool.openapi_json()
    assert f == c


def test_tool_creation_from_function(FuncTool):
    result = FuncTool.openapi_json()

    assert FuncTool.__name__ == "TestTool"
    assert FuncTool.__doc__ == "Tool called TestTool"

    assert result == {
        "type": "function",
        "function": {
            "name": "TestTool",
            "description": "Tool called TestTool",
            "parameters": {
                "type": "object",
                "title": "TestTool",
                "description": "Tool called TestTool",
                "properties": {
                    "value": {
                        "title": "Value",
                        "type": "integer"
                    }
                },
                "required": ["value"]
            }
        }
    }
