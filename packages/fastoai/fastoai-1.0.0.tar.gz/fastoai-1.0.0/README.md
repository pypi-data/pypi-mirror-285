# FastOAI (OpenAI-like API Server)

## Motivation

This project is a simple API server that can be used to serve language models.
It is designed to be simple to use and easy to deploy. It is built using [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/) and [openai-python](https://github.com/openai/openai-python).

## Quick Start

```python
from fastoai import FastOAI
from fastoai.requests import CreateChatCompletionParams

app = FastOAI()


@app.post_chat_completion
def chat_completion(params: CreateChatCompletionParams):
    assert params.model == "gpt-3.5-turbo-0125"
    assert len(params.messages) > 0
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-3.5-turbo-0125",
        "system_fingerprint": "fp_44709d6fcb",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "\n\nHello there, how may I assist you today?",
            },
            "logprobs": None,
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }
```

And that's it! You can now run the server using `uvicorn`:

```bash
uvicorn app:app --reload --port 8000 --host 0.0.0.0
```
