class KittyChatError(Exception):
    pass


class InvalidModel(KittyChatError):
    msg = "MessageDropper only works with chat completion models."
    msg += " Got model {model!r}."

    def __init__(self, model, *args):
        self.model = model
        super().__init__(self.msg.format(model=self.model), *args)


class NotEnoughTokens(KittyChatError):
    msg = "Ran out of messages to drop and we're still {token_count}/{max_tokens}."

    def __init__(self, token_count: int, max_tokens: int, *args):
        self.token_count = token_count
        self.max_tokens = max_tokens
        m = self.msg.format(token_count=token_count, max_tokens=max_tokens)
        super().__init__(m, *args)
