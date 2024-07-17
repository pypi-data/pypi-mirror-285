from typing import Literal, Optional, TypedDict

import pytest

from kittychat.errors import InvalidModel, NotEnoughTokens
from kittychat.msg_dropping import MessageDropper


class ChatMLMessage(TypedDict):
    content: str
    name: Optional[str]
    role: Literal["user", "assistant", "system"]


@pytest.fixture
def message_dropper():
    return MessageDropper("openai/gpt-3.5-turbo")


def test_init_invalid_model():
    with pytest.raises(InvalidModel):
        MessageDropper("openai/text-embedding-ada-002")


def test_single_user_message(message_dropper: MessageDropper):
    thread = [{"content": " kbj"*20000, "role": "user"}]
    with pytest.raises(NotEnoughTokens):
        message_dropper.run(thread)


def test_run_drop_messages(message_dropper: MessageDropper):
    thread = [
        {"content": "Hello, world!", "role": "user"},
        {"content": "How are you?", "role": "assistant"},
        {"content": "I'm fine, thanks."*10000, "role": "user"},
        {"content": "What about you?", "role": "user"},
        {"content": "I'm good too.", "role": "assistant"},
    ]
    result = message_dropper.run(thread)
    assert len(result) == 2
    assert result[0]["content"] == "What about you?"
    assert result[1]["content"] == "I'm good too."
