from fastapi import FastAPI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
)

STREAMING_RESPONSE_EXAMPLE = """\
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-3.5-turbo-0125", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-3.5-turbo-0125", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{"content":"Hello"},"logprobs":null,"finish_reason":null}]}

....

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1694268190,"model":"gpt-3.5-turbo-0125", "system_fingerprint": "fp_44709d6fcb", "choices":[{"index":0,"delta":{},"logprobs":null,"finish_reason":"stop"}]}

data: [DONE]
"""


class FastOAI(FastAPI):
    def create_chat_completions(self):  # type: ignore
        return self.post(
            "/chat/completions",
            responses={
                201: {
                    "content": {
                        "text/plain": {
                            "example": STREAMING_RESPONSE_EXAMPLE,
                        }
                    },
                    "description": "Stream plain text using utf8 charset.",
                    "model": ChatCompletionChunk,
                },
            },
            response_model=ChatCompletion,
        )
