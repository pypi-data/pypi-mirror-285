class ApiError(Exception):
    """The base class for Api related errors."""
    pass

class RegistryNotFoundError(ApiError):
    """
    An error that occurs when the ralium registry was not found.
    Often due to `ralium.api.register()` at the global level of the file
    """
    pass

class ProjectNotFoundError(ApiError):
    """An error that occurs when the specified project directory does not exist."""
    pass

class RoutesNotFoundError(ApiError):
    """An error that occurs when the specified routes directory does not exist."""
    pass

class WebHookError(Exception):
    """The base class for WebHook related errors."""
    pass

class WebHookNotFoundError(WebHookError):
    """
    An error that occurs when trying to render a specific 
    URL that does not have a WebHook attached to it.
    """
    pass

class WebApiError(Exception):
    """The base class for WebApi related errors."""
    pass

class WebBridgeError(WebApiError):
    """
    An error that occurs when a callable is not passed
    to the bridge event wrapper function.
    """
    pass

class SetupError(Exception):
    """The base class for Setup related errors."""
    pass

class WindowError(Exception):
    """The base class for Window related errors."""
    pass

class WindowRuntimeError(WindowError):
    """An error that occurs when the window is not running."""
    pass