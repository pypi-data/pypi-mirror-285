from typing import ClassVar, Optional, Type
from typedtemplate import TypedTemplate, BaseTemplateEngine
from pydantic import BaseModel


class TypedPrompt(BaseModel):
    """
    This is a placeholder class to implement automated prompt engineering with DSPy later.
    """
    static_instructions: ClassVar[Optional[str]] = None
    instructions: Optional[TypedTemplate] = None
    context: Optional[TypedTemplate] = None

    def render(self) -> str:
        if self.instructions is None and self.static_instructions is None:
            raise ValueError("No instructions provided. Both static_instructions and instructions are None. "
                             "One must be provided.")
        ins = self.instructions.render() if self.instructions is not None else self.static_instructions
        ctx = f"\n# Context\n{self.context.render()}" if self.context is not None else ""
        return f"# Instructions \n{ins}{ctx}"

