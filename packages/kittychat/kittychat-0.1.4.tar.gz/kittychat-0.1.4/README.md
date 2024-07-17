# kittychat

The purrfect chat utils library!
With Kittychat, you'll be feline fine as a kittycat, since it ensures your threads stay within the LLMs token limits by whisking away old messages.

## install

`pip install kittychat`

## usage

```python
import logging

from kittychat.msg_dropping import MessageDropper
from kittychat.errors import NotEnoughTokens

thread = [
    {
        "content": "What is the weather like in Boston?",
        "role": "user",
    },
]
functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
            },
            "required": ["location"],
        },
    }
]
model = "openai/gpt-3.5-turbo-0613"

msgd = MessageDropper(model)
length, max_tokens, is_too_big = msgd.check_thread_length(thread, functions)
if is_too_big:
    logging.warn(f"Thread too big: {length} tokens; max is {max_tokens} for model '{model}'.")
try:
    cropped_thread = msgd.run(thread, functions)
except NotEnoughTokens as e:
    raise YourPromptTooBigException(e.token_count, e.max_tokens, model)
return cropped_thread
```
