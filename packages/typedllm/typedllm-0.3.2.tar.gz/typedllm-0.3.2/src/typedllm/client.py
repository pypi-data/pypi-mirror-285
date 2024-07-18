import json
from typing import Type, List, Optional

import pydantic
from typedtemplate import TypedTemplate

from .interop import litellm_request, async_litellm_request
from .tool import ToolCollection, Tool
from .models import (
    LLMSession,
    LLMRequest,
    LLMResponse,
    LLMAssistantMessage,
    LLMAssistantToolCall, LLMModel, LLMUserMessage
)


async def async_request(
        session: LLMSession,
        req: LLMRequest
) -> (LLMSession, LLMResponse):
    # TODO: Add support for a Memory Interface here.
    # Memory can be set as a configuration option and can be invoked here.
    messages = generate_message_json(
        *session.messages,
        *req.tool_results,
        req.message
    )
    tools, tool_choice = generate_tool_json(
        *session.tools, *req.tools,
        force_text_response=req.force_text_response,
        required_tool=req.required_tool
    )
    raw_response = await async_litellm_request(
        session.model.ssl_verify,
        session.model.name,
        session.model.max_retries,
        session.model.api_key,
        messages,
        tools.openapi_json(),
        tool_choice,
        verbose=session.verbose,
        headers=session.model.headers,
        organization=session.model.organization,
        api_base=session.model.api_base
    )

    # This is broken out to support sync/async code paths in the tool calls section
    assistant_message = extract_assistant_message(raw_response)
    tools_calls = await async_extract_tool_calls(raw_response, tools, session)
    response = LLMResponse(
        message=assistant_message,
        tool_calls=tools_calls,
        raw=raw_response
    )

    update_session(session, response)
    return session, response


def request(
        session: LLMSession,
        req: LLMRequest
) -> (LLMSession, LLMResponse):
    # TODO: Add support for a Memory Interface here.
    # Memory can be set as a configuration option and can be invoked here.
    messages = generate_message_json(
        *session.messages,
        *req.tool_results,
        req.message
    )
    tools, tool_choice = generate_tool_json(
        *session.tools, *req.tools,
        force_text_response=req.force_text_response,
        required_tool=req.required_tool
    )
    raw_response = litellm_request(
        session.model.ssl_verify,
        session.model.name,
        session.model.max_retries,
        session.model.api_key,
        messages,
        tools.openapi_json(),
        tool_choice,
        verbose=session.verbose,
        headers=session.model.headers,
        organization=session.model.organization,
        api_base=session.model.api_base
    )

    # This is broken out to support sync/async code paths in the tool calls section
    assistant_message = extract_assistant_message(raw_response)
    tools_calls = sync_extract_tool_calls(raw_response, tools, session)
    response = LLMResponse(
        message=assistant_message,
        tool_calls=tools_calls,
        raw=raw_response
    )

    update_session(session, response)
    return session, response


def update_session(session: LLMSession, response: LLMResponse) -> None:
    # Add tool calls to session messsages
    if response.tool_calls and len(response.tool_calls) > 0:
        for tool_call in response.tool_calls:
            session.messages.append(tool_call)

    # Add messages to the session
    if response.message:
        session.messages.append(response.message)


def generate_message_json(*messages):
    return [msg.openai_json() for msg in messages]


def generate_tool_json(*tools, force_text_response=False, required_tool=None):
    tools = ToolCollection(*tools)
    if len(tools) == 0 or force_text_response:
        tool_choice = "none"
    elif required_tool:
        tool_choice = required_tool.openai_tool_choice_json()
    else:
        tool_choice = "auto"
    return tools, tool_choice


def extract_assistant_message(res) -> Optional[LLMAssistantMessage]:
    from litellm.utils import ModelResponse
    response: ModelResponse = res

    if len(response.choices) != 1:
        raise Exception("Invalid number of choices in response. Expect only one choice.")

    msg = response.choices[0].message

    if msg["role"] != "assistant":
        raise Exception("Invalid role in response")
    if msg.content:
        return LLMAssistantMessage(
            content=msg.content,
        )
    return None


async def async_extract_tool_calls(
        res,  # LiteLLM Response
        tools: ToolCollection,
        session: LLMSession,
        max_depth: int = 3
) -> List[LLMAssistantToolCall]:
    msg = res.choices[0].message
    tool_calls = []
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        for tool_call in msg["tool_calls"]:
            ToolClz = tools.get_by_name(tool_call.function.name)
            tool = await async_tool_from_json_str(
                session,
                tool_call.function.arguments,
                ToolClz,
                max_depth=max_depth
            )
            tc = LLMAssistantToolCall(
                id=tool_call.id,
                tool=tool,
                args=tool_call.function.arguments
            )
            tool_calls.append(tc)
    return tool_calls


def sync_extract_tool_calls(
        res,
        tools: ToolCollection,
        session: LLMSession,
        max_depth: int = 3
) -> List[LLMAssistantToolCall]:
    msg = res.choices[0].message
    tool_calls = []
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        for tool_call in msg["tool_calls"]:
            ToolClz = tools.get_by_name(tool_call.function.name)
            tool = sync_tool_from_json_str(
                session,
                tool_call.function.arguments,
                ToolClz,
                max_depth=max_depth
            )
            tc = LLMAssistantToolCall(
                id=tool_call.id,
                tool=tool,
                args=tool_call.function.arguments
            )
            tool_calls.append(tc)
    return tool_calls


def typed_request(model: LLMModel, template: Type[TypedTemplate], tool: Type[Tool], **kwargs):
    msg = template(**kwargs).render()
    session = LLMSession(model=model)
    req = LLMRequest(
        tools=[tool],
        required_tool=tool,
        message=LLMUserMessage(content=msg)
    )
    _, response = request(session, req)
    tool_response = response.tool_calls[0].tool
    return tool_response


async def async_typed_request(model: LLMModel, template: Type[TypedTemplate], tool: Type[Tool], **kwargs):
    msg = template(**kwargs).render()
    session = LLMSession(model=model)
    req = LLMRequest(
        tools=[tool],
        required_tool=tool,
        message=LLMUserMessage(content=msg)
    )
    _, response = await async_request(session, req)
    tool_response = response.tool_calls[0].tool
    return tool_response


async def async_tool_from_json_str(session: LLMSession, json_str: str, ToolClz: Type[Tool], depth: int = 0, max_depth: int = 3) -> Tool:
    try:
        argument_dict = json.loads(json_str)
        tool = ToolClz(**argument_dict)
        return tool
    except (json.JSONDecodeError, pydantic.ValidationError) as e:
        if depth >= max_depth:
            raise Exception("Invalid Tool JSON. Max depth reached.")

        msg = f"""# Instructions
        You must fix the invalid JSON provided to match the tool.
        Use the error message below to fix the JSON.
        
        # JSON
        {json_str}
        
        # Error
        {str(e)}
        """
        tools, tool_choice = generate_tool_json(
            ToolClz,
            force_text_response=False,
            required_tool=ToolClz
        )
        response = await async_litellm_request(
            session.model.ssl_verify,
            session.model.name,
            session.model.max_retries,
            session.model.api_key,
            generate_message_json(LLMUserMessage(content=msg)),
            tools.openapi_json(),
            tool_choice,
            verbose=session.verbose,
            headers=session.model.headers,
            organization=session.model.organization,
            api_base=session.model.api_base
        )
        return await async_tool_from_json_str(
            session,
            response.choices[0].message.tool_calls[0].function.arguments,
            ToolClz,
            depth + 1,
            max_depth
        )


def sync_tool_from_json_str(session: LLMSession, json_str: str, ToolClz: Type[Tool], depth: int = 0, max_depth: int = 3) -> Tool:
    try:
        argument_dict = json.loads(json_str)
        tool = ToolClz(**argument_dict)
        return tool
    except (json.JSONDecodeError, pydantic.ValidationError) as e:
        if depth >= max_depth:
            raise Exception("Invalid Tool JSON. Max depth reached.")

        msg = f"""# Instructions
        You must fix the invalid JSON provided to match the tool.
        Use the error message below to fix the JSON.

        # JSON
        {json_str}

        # Error
        {str(e)}
        """
        tools, tool_choice = generate_tool_json(
            ToolClz,
            force_text_response=False,
            required_tool=ToolClz
        )
        response = litellm_request(
            session.model.ssl_verify,
            session.model.name,
            session.model.max_retries,
            session.model.api_key,
            generate_message_json(LLMUserMessage(content=msg)),
            tools.openapi_json(),
            tool_choice,
            verbose=session.verbose,
            headers=session.model.headers,
            organization=session.model.organization,
            api_base=session.model.api_base
        )
        return sync_tool_from_json_str(
            session,
            response.choices[0].message.tool_calls[0].function.arguments,
            ToolClz,
            depth + 1,
            max_depth
        )
