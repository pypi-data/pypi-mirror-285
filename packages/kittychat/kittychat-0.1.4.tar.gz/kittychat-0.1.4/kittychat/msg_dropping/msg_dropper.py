"""
Drop old messages from a thread if the thread is too long.

"""

import logging
from typing import Optional

from totokenizers.factories import Totokenizer, TotoModelInfo
from totokenizers.model_info import ChatModelInfo
from totokenizers.schemas import Chat

from ..errors import InvalidModel, NotEnoughTokens

logger = logging.getLogger(__name__)


class MessageDropper:
    def __init__(self, model: str):
        self.tokenizer = Totokenizer.from_model(model)
        self.model_info = TotoModelInfo.from_model(model)
        if not isinstance(self.model_info, ChatModelInfo):
            raise InvalidModel(self.tokenizer.model)

    def run(
        self,
        thread: Chat,
        functions: Optional[list[dict]] = None,
        desired_max_tokens: int = 50,
    ) -> Chat:
        """
        Drop enough messages so the token count is below the model's maximum.

        Skip the system message, as that's always the first message.
        """
        logger.info("Running MessageDropper on thread: %s", len(thread))
        thread = thread.copy()
        if len(thread) == 0 or not desired_max_tokens:
            return thread

        index = 1 if thread[0]["role"] == "system" else 0
        thread_tokens = self.tokenizer.count_chatml_tokens(thread, functions)
        token_count = thread_tokens + desired_max_tokens
        while token_count > self.model_info.max_tokens:
            logger.debug(
                "Thread has %d tokens, which is more than the maximum of %d",
                token_count,
                self.model_info.max_tokens,
            )
            if len(thread) == 1:
                raise NotEnoughTokens(token_count, self.model_info.max_tokens)
            if len(thread) == 2:
                if thread[0]["role"] == "system":
                    raise NotEnoughTokens(token_count, self.model_info.max_tokens)
                else:
                    thread.pop(0)
                    continue
            logger.debug("Dropping message: %s", thread[1])
            thread.pop(index)
            thread_tokens = self.tokenizer.count_chatml_tokens(thread, functions)
            token_count = thread_tokens + desired_max_tokens

        logger.debug("Finished running MessageDropper on thread: %s", len(thread))
        return thread

    def check_thread_length(
        self,
        thread: Chat,
        functions: Optional[list[dict]] = None,
        desired_max_tokens: int = 50,
    ) -> tuple[int, int, bool]:
        """
        Check if a thread is too big for the model.
        """
        thread_length = self.tokenizer.count_chatml_tokens(thread, functions)
        thread_length += desired_max_tokens
        toobig = thread_length > self.model_info.max_tokens
        return thread_length, self.model_info.max_tokens, toobig
