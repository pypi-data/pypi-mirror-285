"""Custom exceptions for the Hermes engine."""


class InvalidPromptError(Exception):
    """Invalid prompt error."""


class TokenLimitExceededError(Exception):
    """Token limit exceeded error."""


class MessageStartIdxNotFound(Exception):
    """Message start index not found error."""


class MissingContextData(Exception):
    """Missing context data error."""
