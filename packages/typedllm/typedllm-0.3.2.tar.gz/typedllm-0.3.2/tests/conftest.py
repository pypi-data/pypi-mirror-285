from typing import ClassVar

import os
import pytest

from typedllm import LLMModel, TypedPrompt, LLMSession, LLMRequest, Tool, create_tool_from_function
from typedtemplate import JinjaTemplateEngine, TypedTemplate
from pydantic import Field


@pytest.fixture(name="openai_key")
def get_openai_key() -> str:
    return os.getenv("OPENAI_API_KEY")


@pytest.fixture(name="model")
def fixture_model(openai_key: str) -> LLMModel:
    return LLMModel(
        name="gpt-4",
        api_key=openai_key,
    )


@pytest.fixture(name="prompt")
def get_prompt_value():
    return {
        "system": "You are an AI assistant. You must respond to questions and follow all instructions.",
        "prompt": "Please respond with just 'Hi' to this message"
    }


@pytest.fixture(name="hi_acompletion")
def hi_acompletion():
    return {"choices": [{"text": "Hi"}]}


@pytest.fixture(name="jinja_engine")
def get_template_engine():
    return JinjaTemplateEngine()


@pytest.fixture(name="llmprompt")
def get_prompt(jinja_engine: JinjaTemplateEngine):
    class PromptTemplate(TypedTemplate):
        template_engine = jinja_engine
        template_string = "What year was {{ city }} founded?"
        city: str = Field(description="The city to use in the prompt")

    return PromptTemplate


@pytest.fixture(name="instruction_template")
def get_instruction_template(jinja_engine: JinjaTemplateEngine):
    class InstructionTemplate(TypedTemplate):
        template_engine = jinja_engine
        template_string = "What year was {{ city }} founded?"
        city: str = Field(description="City name")
    return InstructionTemplate


@pytest.fixture(name="context_template")
def get_context_template(jinja_engine: JinjaTemplateEngine):
    class ContextTemplate(TypedTemplate):
        template_engine = jinja_engine
        template_string = "User Name: {{ username }}"
        username: str = Field(description="User's name")
    return ContextTemplate

@pytest.fixture(name="llmsession")
def get_session(model: LLMModel) -> LLMSession:
    return LLMSession(
        model=model,
        verbose=True,
    )


@pytest.fixture(name="llmrequest")
def get_request():
    return LLMRequest(force_text_response=True)


@pytest.fixture(name="llmtool")
def get_tool():
    class CityFoundingTool(Tool):
        """A tool to collect a city and its founding year."""
        city_name: str = Field(description="The name of the city")
        founded_year: int = Field(description="The year a city was founded")
    return CityFoundingTool


@pytest.fixture(name="FuncTool")
def get_function_tool():
    def TestTool(value: int) -> str:
        return str(value)
    return create_tool_from_function(TestTool)


@pytest.fixture(name="ClassTool")
def get_class_tool():
    class TestTool(Tool):
        value: int
    return TestTool
