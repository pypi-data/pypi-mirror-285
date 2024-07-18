import inspect
from typing import Type, Callable, List
from pydantic import BaseModel, Field, create_model


class Tool(BaseModel):
    """LLM Tool that can be used in a request"""
    def __call__(self) -> any:
        """
        Implement this function to make the tool callable.
        :return:
        """
        raise NotImplementedError("The __call__ method is not implemented for the Tool class.")

    @classmethod
    def openai_tool_choice_json(cls):
        return {
            "type": "function",
            "function": {
                "name": cls.__name__,
            }
        }

    @classmethod
    def openapi_json(cls):
        name = cls.__name__
        description = cls.__doc__ or f"Tool called {cls.__name__}"
        if cls.__doc__ is None:
            # Patch docstring so Tool classes and functions act the same. See unit tests.
            cls.__doc__ = description
        schema = cls.model_json_schema()
        result = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": schema
            }
        }
        return result


StringClass = "a".__class__


def create_tool_from_function(
        function: Callable,
) -> Type[Tool]:
    sig = inspect.signature(function)
    annotations = {}
    for name, param in sig.parameters.items():
        if param.annotation is param.empty:
            raise ValueError(f"Parameter {name} does not have a type hint")
        annotations[name] = (param.annotation, Field(...))

    def call_function(self):
        item_name = list(self.model_fields_set)[0]
        value = getattr(self, item_name)
        return function(value)

    ToolClz: Type[Tool] = create_model(
        function.__name__,
        **annotations,
        __base__=(Tool,),
        __doc__=function.__doc__ or f"Tool called {function.__name__}",
        __call__=call_function
    )
    return ToolClz


class ToolCollection(List[Type[Tool]]):
    def __init__(self, *args):
        super().__init__(args)

    def openapi_json(self):
        return [tool.openapi_json() for tool in self]

    def get_by_name(self, name: str) -> Type[Tool]:
        for tool in self:
            if tool.__name__ == name:
                return tool
        raise ValueError(f"Tool with name {name} not found.")
