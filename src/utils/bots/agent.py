import os
from collections.abc import Callable, Generator

from google import genai
from google.genai import types

from utils.bots.ctx_mgr import CtxMgr
from utils.function_call.pets import (
    cawling_dcard_urls,
    crawling_dcard_article_content,
    get_awaiting_adoption_pet_info,
)
from utils.helpers import (
    error_badge,
    str_stream,
    success_badge,
)
from utils.i18n import i18n


def func_call_result_badge_stream(func_call_result: dict) -> Generator:
    """
    Stream a badge indicating function call success or error, character by
    character.

    Arguments:
        func_call_result (dict): Contains "status" and "func_call" info.

    Yields:
        str: Characters forming the status badge message.
    """
    func_call_msg_i18n_key = f"pets.chat.badge.func_call_{func_call_result['status']}"
    func_call_msg = i18n(func_call_msg_i18n_key).format(
        func_name=func_call_result["func_call"].name
    )

    if func_call_result["status"] == "error":
        print(f"Error in function call: {func_call_result['result']}")
        yield from str_stream(error_badge(func_call_msg))
    else:
        yield from str_stream(success_badge(func_call_msg))


class Agent:
    def __init__(
        self,
        config: types.GenerateContentConfig,
        ctx_content: CtxMgr,
        func_maps: dict[str, Callable],
    ) -> None:
        self.config = config
        self.func_maps = func_maps
        self.ctx_content = ctx_content

        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def execute_func_call(self, func_call: types.FunctionCall) -> dict:
        """
        Execute the given function call, capture success or error, and return status
        and result.

        Arguments:
            func_call (types.FunctionCall): Function call object to execute

        Returns:
            dict: {
                "func_call": FunctionCall,
                "status": "success" or "error",
                "result": Function result or error message
            }
        """
        func_call_result = {
            "func_call": func_call,
            "status": "unknown",
            "result": "unknown",
        }

        try:
            if func_call.name == "get_awaiting_adoption_pet_info":
                func_call_result["status"] = "success"
                func_call_result["result"] = get_awaiting_adoption_pet_info()
            elif func_call.name == "cawling_dcard_urls":
                func_call_result["status"] = "success"
                func_call_result["result"] = cawling_dcard_urls(**func_call.args)
            elif func_call.name == "crawling_contents":
                func_call_result["status"] = "success"
                func_call_result["result"] = crawling_dcard_article_content(
                    **func_call.args
                )
            # XXX: Extension point for other function calls
            else:
                raise ValueError(f"Unknown function call: {func_call.name}")
        except Exception as e:
            func_call_result["status"] = "error"
            func_call_result["result"] = str(e)

        return func_call_result

    def gemini_function_calling(
        self,
        function_calls: list[types.FunctionCall],
    ) -> Generator:
        """
        Process a list of function calls: execute each, stream its badge, then prompt for next
        actions and continue with model response.

        Arguments:
            function_calls (list[types.FunctionCall]): FunctionCall objects to process.

        Yields:
            str: Characters of badge messages and subsequent model response.
        """
        for func_call in function_calls:
            func_call_result = self.execute_func_call(func_call)
            self.add_func_call_result(func_call_result)

            return func_call_result_badge_stream(func_call_result)

        return self.gemini_response_stream()

    def gemini_response_stream(self, config: dict) -> Generator:
        """
        Invoke the Gemini client to stream text chunks from the model, yield them, and
        record the full response and handle any function calls.

        Yields:
            str: Characters from the model's response and streams function call handling if needed.
        """
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        function_calls = []
        this_response = ""

        for chunk in client.models.generate_content_stream(**config):
            print(f"{chunk.text=}")
            if chunk.text is not None:
                this_response += chunk.text
                return chunk.text
            elif chunk.function_calls:
                function_calls.extend(chunk.function_calls)

        self.ctx_content.add_context(
            types.Content(
                role="model", parts=[types.Part.from_text(text=this_response)]
            )
        )

        if function_calls:
            return self.gemini_function_calling(function_calls)
