__all__ = [
    "NotSupportedError",
    "InvalidArgumentError",
    "PlatynUiException",
    "PlatyUiError",
    "PlatynUiFatalError",
    "AdapterNotValidError",
    "AdapterNotFoundError",
    "AdapterNotFoundFatalError",
    "NotAStrategyTypeError",
    "AdapterNotSupportsStrategyError",
    "CannotEnsureError",
    "NoKeyboardProxyError",
    "NoMouseProxyError",
    "NoDisplayProxyError",
    "NoLocatorDefinedError",
]


class NotSupportedError(Exception):
    pass


class InvalidArgumentError(Exception):
    pass


class PlatynUiException(Exception):  # noqa: N818
    pass


class PlatyUiError(PlatynUiException):
    pass


class PlatynUiFatalError(PlatynUiException):
    pass


class AdapterNotValidError(PlatynUiException):
    pass


class AdapterNotFoundError(PlatynUiException):
    pass


class AdapterNotFoundFatalError(PlatynUiFatalError):
    pass


class NotAStrategyTypeError(PlatyUiError):
    pass


class AdapterNotSupportsStrategyError(PlatyUiError):
    pass


class CannotEnsureError(PlatyUiError):
    pass


class NoKeyboardProxyError(PlatyUiError):
    pass


class NoDisplayProxyError(PlatyUiError):
    pass


class NoMouseProxyError(PlatyUiError):
    pass


class NoLocatorDefinedError(PlatyUiError):
    pass
