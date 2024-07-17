from ralium.util.common import RALIUM_API_REGISTRY_IDENTIFIER
from ralium.web.webhook import WebHook, create_namespace
from ralium.window import Window

from ralium.util.exceptions import (
    RegistryNotFoundError,
    ProjectNotFoundError,
    RoutesNotFoundError,
    ApiError
)

from ralium.util.common import (
    get_bundled_filesystem, 
    normalize_webhook_url,
    read_file_contents,
    check_path_exists,
    check_path_is_dir,
    check_bundled,
    is_function,
    create_path
)

from pathlib import Path

import inspect
import os

def check_project_path(project):
    if not check_path_exists(project):
        raise ProjectNotFoundError(f"failed to find project directory. ('{project}')")
    
    if not check_path_is_dir(project):
        raise ApiError("Project path must lead to a directory.")

def check_routes_path(routes):
    if not check_path_exists(routes):
        raise RoutesNotFoundError("Project directory must contain a routes directory.")
    
    if not check_path_is_dir(routes):
        raise ApiError("Project routes path must lead to a directory.")

def collect_project_shared_styles(project):
    styles_path = project/"styles"
    styles = []

    if not check_path_exists(styles_path) or not check_path_is_dir(styles_path):
        return []

    for root, _, files in os.walk(styles_path):
        styles.extend([Path(root, file).absolute() for file in files if Path(file).suffix == ".css"])
    
    return styles

def get_server_registry_contents(source):
    globals = {}
    exec(read_file_contents(source), globals)
    return globals.get(RALIUM_API_REGISTRY_IDENTIFIER, [])

def get_server_registry_objects(source):
    functions = []
    namespaces = []

    for obj in get_server_registry_contents(source):
        if isinstance(obj, WebHook.Namespace):
            namespaces.append(obj)
            continue

        if is_function(obj):
            functions.append(obj)
    
    return functions, namespaces

if check_bundled():
    def collect_webhooks(_, __):
        filesystem = get_bundled_filesystem()

        webhooks = []
        shared_styles = [str(style) for style in filesystem.styles]

        for bundle in filesystem.bundles:
            styles = [*shared_styles, *[str(style) for style in bundle.styles]]

            functions = []
            namespaces = []

            if bundle.server is not None:
                functions, namespaces = get_server_registry_objects(bundle.server.relpath)
            
            webhooks.append(WebHook(bundle.url, str(bundle.page), styles, functions, namespaces))
        
        return webhooks
else:
    def collect_webhooks(project, routes):
        webhooks = []

        shared_styles = collect_project_shared_styles(project)
        root_prefix = str(project/"routes")

        for root, _, files in os.walk(routes):
            # Skip empty directories
            if not files or Path(root).name == "__pycache__":
                continue

            url = normalize_webhook_url(root.removeprefix(root_prefix))
            html = None
            styles = [*shared_styles]
            functions = []
            namespaces = []

            for file in files:
                file = Path(file)
                path = Path(root, file)

                if file.name == "+page.html":
                    html = path
                elif file.suffix == ".css":
                    styles.append(path)
                elif file.name == "+server.py":
                    functions, namespaces = get_server_registry_objects(path)
            
            if html is None:
                raise ApiError(f"All routes must contain a '+page.html' file. ('{root}')")
            
            webhooks.append(WebHook(url, html, styles, functions, namespaces))
    
        return webhooks

class Module:
    """
    A container, typically used for module methods, that wraps functions and named functions that don't need a window argument.

    :param functions: A list of functions or methods to wrap.
    :param named_functions: A dictionary of functions with names different from their current ones to wrap.
    """

    # Flag attribute used by the 'WebHook.Namespace' class.
    _module_api_class = True
    
    def __init__(self, *functions, **named_functions):
        self.functions = [wrap(function) for function in functions]
        self.named_functions = {name: wrap(function) for name, function in named_functions.items()}

def create_window(project, config = None):
    """
    Creates a window from a specific directory structure.

    :param project: The project directory.
    :param config: The window configuration.

    :returns: A `Window` object.

    :raises ApiError: If the `project` or `routes` paths are not directories.
    :raises ProjectNotFoundError: If the project directory was not found.
    :raises RoutesNotFoundError: If the routes directory was not found.
    """

    project = create_path(project)
    routes = project/"routes"

    check_project_path(project)
    check_routes_path(routes)

    webhooks = collect_webhooks(project, routes)

    return Window(webhooks, config)

def register():
    """
    Creates a registry list to expose functions and namespaces for use within JavaScript.

    :returns: A decorator for exposing Python functions to JavaScript.
    """

    globals = inspect.currentframe().f_back.f_globals
    globals[RALIUM_API_REGISTRY_IDENTIFIER] = []

    def wrapper(function):
        if not is_function(function):
            raise ApiError("Expose decorator must be called on a 'function' object.")

        if function not in globals[RALIUM_API_REGISTRY_IDENTIFIER]:
            globals[RALIUM_API_REGISTRY_IDENTIFIER].append(function)
        
        def echo(*args, **kwargs):
            return function(*args, **kwargs)
        
        echo.__name__     = function.__name__
        echo.__qualname__ = function.__qualname__
        echo.__function__ = function

        return echo

    return wrapper

def namespace(alias, *functions, **named_functions):
    """
    Adds a namespace to the server registry.

    :param alias: The name the namespace is accessed by.
    :param functions: A list of functions to add.
    :param named_functions: A dictionary of functions to add.

    :returns: A `WebHook.Namespace` object.

    :raises RegistryNotFoundError: If `ralium.api.register` is not called at the global level.

    The alias of the regularly listed functions will be the value
    of the `__name__` property of the function objects.

    The alias of the named function dictionary will be the keyword part.
    """

    registry = inspect.currentframe().f_back.f_globals.get(RALIUM_API_REGISTRY_IDENTIFIER)

    if registry is None:
        raise RegistryNotFoundError(
            "No active registry found in the global space.",
            "Ensure that 'ralium.api.register' has been called to initialize the registry.",
            "('ralium.api.register' must be called at the global level of the file)"
        )
    
    for function in [*functions, *named_functions.values()]:
        if hasattr(function, "__function__"):
            function = getattr(function, "__function__")
        
        if function in registry:
            raise ApiError(f"Cannot add already exposed function '{function.__name__}' to a namespace.")
    
    registry.append(create_namespace(alias, *functions, **named_functions))

def wrap(function):
    """
    Wraps a function to accept a 'window' argument, typically for module methods.
    The wrapped function does not get the `Window` object passed to it.

    :param function: A function or method.

    :returns: A decorator for the wrapped function.
    """

    def wrapper(_, *args, **kwargs):
        return function(*args, **kwargs)
    
    wrapper.__name__     = function.__name__
    wrapper.__qualname__ = function.__qualname__
    
    return wrapper