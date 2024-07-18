from typedtemplate import TypedTemplate
from typing import Type
from typedllm import TypedPrompt


def test_basic_prompt(instruction_template: Type[TypedTemplate], context_template: Type[TypedTemplate]):
    class TestPrompt(TypedPrompt):
        instructions: instruction_template
        context: context_template

    prompt = TestPrompt(
        instructions=instruction_template(city="San Francisco"),
        context=context_template(username="Johnny Test")
    )
    result = prompt.render()
    assert result is not None
    assert result == "# Instructions \nWhat year was San Francisco founded?\n# Context\nUser Name: Johnny Test"


def test_static_instructions(context_template: Type[TypedTemplate]):
    class TestPrompt(TypedPrompt):
        static_instructions = "What year was San Francisco founded?"
        context: context_template

    prompt = TestPrompt(
        context=context_template(username="Johnny Test")
    )
    result = prompt.render()
    assert result is not None
    assert result == "# Instructions \nWhat year was San Francisco founded?\n# Context\nUser Name: Johnny Test"
