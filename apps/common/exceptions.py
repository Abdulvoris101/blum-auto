from typing import Optional


class AiogramException(Exception):
    def __init__(self, userId, message_text, original_exception=None):
        self.userId = userId
        self.message_text = message_text
        self.original_exception = original_exception


class InternalServerException(Exception):
    def __init__(self, message_text, original_exception=None):
        self.message_text = message_text
        self.original_exception = original_exception


class NullPointerException(Exception):
    def __init__(self, message_text, original_exception=None):
        self.message_text = message_text
        self.original_exception = original_exception


class ForbiddenException(Exception):
    def __init__(self, chatId, messageText, original_exception=None):
        self.userId = chatId
        self.message_text = messageText
        self.original_exception = original_exception


class InvalidRequestException(Exception):
    def __init__(self, messageText: str, exceptionText: str = ''):
        self.messageText = messageText
        self.exceptionText = exceptionText
