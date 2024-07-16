import functools
import inspect
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, TypeVar, Union

import openai
import openai.types.chat as openai_types
from betterproto import Casing
from openai.types import ChatModel

import maitai_gen.chat as chat_types
from maitai_common.utils.proto_utils import openai_messages_to_proto

CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def required_args(*variants: Sequence[str]) -> Callable[[CallableT], CallableT]:
    def inner(func: CallableT) -> CallableT:
        params = inspect.signature(func).parameters
        positional = [
            name
            for name, param in params.items()
            if param.kind
               in {
                   param.POSITIONAL_ONLY,
                   param.POSITIONAL_OR_KEYWORD,
               }
        ]

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            given_params: set[str] = set()
            for i, _ in enumerate(args):
                try:
                    given_params.add(positional[i])
                except IndexError:
                    raise TypeError(
                        f"{func.__name__}() takes {len(positional)} argument(s) but {len(args)} were given"
                    ) from None

            for key in kwargs.keys():
                given_params.add(key)

            for variant in variants:
                matches = all((param in given_params for param in variant))
                if matches:
                    break
            else:  # no break
                if len(variants) > 1:
                    variations = human_join(
                        ["(" + human_join([quote(arg) for arg in variant], final="and") + ")" for variant in variants]
                    )
                    msg = f"Missing required arguments; Expected either {variations} arguments to be given"
                else:
                    assert len(variants) > 0

                    # TODO: this error message is not deterministic
                    missing = list(set(variants[0]) - given_params)
                    if len(missing) > 1:
                        msg = f"Missing required arguments: {human_join([quote(arg) for arg in missing])}"
                    else:
                        msg = f"Missing required argument: {quote(missing[0])}"
                raise TypeError(msg)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return inner


# copied from https://github.com/Rapptz/RoboDanny
def human_join(seq: Sequence[str], *, delim: str = ", ", final: str = "or") -> str:
    size = len(seq)
    if size == 0:
        return ""

    if size == 1:
        return seq[0]

    if size == 2:
        return f"{seq[0]} {final} {seq[1]}"

    return delim.join(seq[:-1]) + f" {final} {seq[-1]}"


def quote(string: str) -> str:
    """Add single quotation marks around the given string. Does *not* do any escaping."""
    return f"'{string}'"


def convert_openai_chat_completion(chat: openai_types.ChatCompletion) -> chat_types.ChatCompletionResponse:
    return chat_types.ChatCompletionResponse().from_dict(chat.to_dict())


def _copy_choice(choice: Union[openai_types.chat_completion.Choice, chat_types.ChatCompletionChoice]) -> chat_types.ChatCompletionChoice:
    message = chat_types.ChatMessage(content=choice.message.content, role=choice.message.role)
    copied_choice = chat_types.ChatCompletionChoice(finish_reason=choice.finish_reason, index=choice.index,
                                                    logprobs=choice.logprobs, message=message)
    return copied_choice


def convert_open_ai_chat_completion_chunk(chunk: openai_types.ChatCompletionChunk) -> chat_types.ChatCompletionChunk:
    return chat_types.ChatCompletionChunk().from_dict(chunk.to_dict())


def get_chat_completion_params(*,
                               messages: Iterable[openai_types.ChatCompletionMessageParam],
                               model: Union[str, ChatModel],
                               frequency_penalty: Union[Optional[float], openai.NotGiven] = openai.NOT_GIVEN,
                               logit_bias: Union[Optional[Dict[str, int]], openai.NotGiven] = openai.NOT_GIVEN,
                               logprobs: Union[Optional[bool], openai.NotGiven] = openai.NOT_GIVEN,
                               max_tokens: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
                               n: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
                               presence_penalty: Union[Optional[float], openai.NotGiven] = openai.NOT_GIVEN,
                               response_format: Union[openai_types.completion_create_params.ResponseFormat, openai.NotGiven] = openai.NOT_GIVEN,
                               seed: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
                               stop: Union[Union[Optional[str], List[str]], openai.NotGiven] = openai.NOT_GIVEN,
                               stream: Optional[bool] = False,
                               stream_options: Union[Optional[openai_types.ChatCompletionStreamOptionsParam], openai.NotGiven] = openai.NOT_GIVEN,
                               temperature: Union[Optional[float], openai.NotGiven] = openai.NOT_GIVEN,
                               tool_choice: Union[openai_types.ChatCompletionToolChoiceOptionParam, openai.NotGiven] = openai.NOT_GIVEN,
                               tools: Union[Iterable[openai_types.ChatCompletionToolParam], openai.NotGiven] = openai.NOT_GIVEN,
                               top_logprobs: Union[Optional[int], openai.NotGiven] = openai.NOT_GIVEN,
                               top_p: Union[Optional[float], openai.NotGiven] = openai.NOT_GIVEN,
                               user: Union[str, openai.NotGiven] = openai.NOT_GIVEN,
                               ) -> chat_types.ChatCompletionParams:
    params = chat_types.ChatCompletionParams(
        messages=openai_messages_to_proto(messages),
        model=model,
        stream=stream,
    )
    # Define all optional parameters in a dictionary
    optional_params = {
        'max_tokens': max_tokens,
        'temperature': temperature,
        'top_p': top_p,
        'stop': stop,
        'logprobs': logprobs,
        'top_logprobs': top_logprobs,
        'n': n,
        'seed': seed,
        'logit_bias': logit_bias,
        'presence_penalty': presence_penalty,
        'frequency_penalty': frequency_penalty,
        'user': user,
        'tool_choice': tool_choice,
    }
    # Set each parameter that is not marked as NOT_GIVEN
    for param_name, value in optional_params.items():
        if value != openai.NOT_GIVEN:
            setattr(params, param_name, value)

    if stream_options != openai.NOT_GIVEN and stream_options:
        params.stream_options = chat_types.StreamOptions(include_usage=stream_options.get("include_usage"))

    if response_format != openai.NOT_GIVEN:
        params.response_format = chat_types.ResponseFormat(type=response_format["type"])

    if tools != openai.NOT_GIVEN:
        params.tools = []
        for tool in tools:
            function = tool.get("function")
            params.tools.append(
                chat_types.Tool(
                    type=tool["type"],
                    function=chat_types.Function(
                        name=function.get("name"),
                        description=function.get("description"),
                        parameters=function.get("parameters")
                    )
                )
            )
    return params


def chat_completion_chunk_to_response(final_chunk: chat_types.ChatCompletionChunk, content: Union[str, List[chat_types.ChatMessage]]):
    chat_completion_response = chat_types.ChatCompletionResponse().from_dict(final_chunk.to_dict(casing=Casing.SNAKE))
    if isinstance(content, str):
        chat_completion_response.choices[0].message = chat_types.ChatMessage(role='assistant', content=content)
    if isinstance(content, List):
        chat_completion_response.choices[0].message = content[-1]
    return chat_completion_response
