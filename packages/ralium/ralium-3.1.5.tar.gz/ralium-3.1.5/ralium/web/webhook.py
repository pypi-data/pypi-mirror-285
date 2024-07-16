from ralium.util.common import (
    _raise_if_not_path_type,
    normalize_system_path,
    normalize_webhook_url,
    read_file_contents,
    check_path_exists,
    get_type_name,
    is_function
)

from ralium.util.exceptions import (
    WebHookNotFoundError, 
    WebHookError
)

from collections.abc import Iterable
from pathlib import Path

def create_namespace(alias, *functions, **named_functions):
    """
    Adds a `WebHook.Namespace` object to JavaScript.

    :param alias: The name the namespace is accessed by.
    :param functions: A list of functions to add.
    :param named_functions: A dictionary of functions to add.

    :returns: A `WebHook.Namespace` object.

    The alias of the regularly listed functions will be the value
    of the `__name__` property of the function objects.

    The alias of the named function dictionary will be the keyword part.
    """
    return WebHook.Namespace(alias, *functions, **named_functions)

class WebHook:
    """
    A WebHook Object that contains information for handling a specific URL.

    :param url: The URL that the WebHook handles.
    :param html: A file path or raw text of the HTML to render.
    :param styles: A list or tuple of paths or raw css content.
    :param functions: Functions to expose to JavaScript.
    :param namespaces: Namespaces to expose to JavaScript.
    :param homepage: If this WebHook is a homepage, it will be the fallback page if something goes wrong with the `Navigation` handler.
    :param encoding: The file encoding of the HTML and CSS files.
    """

    class Function:
        def __new__(cls, function, window):
            def wrapper(*args, **kwargs):
                return function(window, *args, **kwargs)
            
            wrapper.__name__     = function.__name__
            wrapper.__qualname__ = function.__name__
            wrapper.__webhook__  = True

            return wrapper

    class Namespace(dict):
        def __init__(self, alias, *functions, **named_functions):
            self.alias = alias

            self.add_functions(*functions)
            self.add_named_functions(**named_functions)
        
        def add(self, name, function):
            if not is_function(function):
                raise TypeError(f"Expected a 'function' object for namespace, instead got '{get_type_name(function)}'")
            
            self.__setitem__(name, function)
        
        def add_functions(self, *functions):
            for function in functions:
                self.add(function.__name__, function)
        
        def add_named_functions(self, **functions):
            for name, function in functions.items():
                self.add(name, function)
    
    class Collection(dict):
        """A helper class for storing `WebHook` objects."""
        
        def __init__(self, *webhooks):
            for webhook in webhooks:
                if not isinstance(webhook, WebHook):
                    raise TypeError("WebHook.Collection can only contain 'WebHook' objects.")

                self[webhook.url] = webhook

        def __iter__(self):
            return self.values().__iter__

        def __repr__(self):
            return f"{{{', '.join([repr(webhook) for webhook in self.values()])}}}"
        
        def get(self, url):
            webhook = super().get(url, None)

            if webhook is None:
                raise WebHookNotFoundError(f"Failed to find WebHook for the url '{url}'")

            return webhook

    def __init__(self, url, html, styles=None, functions=None, namespaces=None, encoding="UTF-8"):
        # Needs to be initialized before html, and styles
        self.encoding = encoding

        self.url = normalize_webhook_url(url)
        self.html = html
        self.styles = styles or []

        self.window = None
        self.elements = []
        self.functions = functions or []
        self.namespaces = namespaces or []

    def __repr__(self):
        return f"WebHook(url='{self.url}')"

    @property
    def html(self):
        return self._html
    
    @property
    def styles(self):
        return self._styles
    
    @html.setter
    def html(self, new_html):
        if isinstance(new_html, bytes):
            new_html = new_html.decode(self.encoding)

        if isinstance(new_html, Path):
            self._html = WebHook.load_html(new_html, self.encoding)
            return
        elif isinstance(new_html, str):
            # Assume if the starting line is <!DOCTYPE html> that it is raw HTML.
            if new_html.startswith("<!DOCTYPE html>"):
                self._html = new_html
                return

            path = Path(new_html)

            if check_path_exists(path):
                self._html = WebHook.load_html(path, self.encoding)
                return
            
            self._html = new_html
            return
        
        raise TypeError(f"WebHook HTML property expected 'Path', 'str' or 'bytes' object, instead got '{get_type_name(new_html)}'")
    
    @styles.setter
    def styles(self, new_styles):
        if not isinstance(new_styles, Iterable):
            raise TypeError(f"WebHook styles property expected an iterable, instead got '{get_type_name(new_styles)}'")
        
        _styles = []

        for style in new_styles:
            if isinstance(style, bytes):
                style = style.decode(self.encoding)

            if isinstance(style, str):
                path = Path(style)

                if not check_path_exists(path):
                    _styles.append(style)
                    continue

                _styles.append(WebHook.load_style(path, self.encoding))
                continue

            if isinstance(style, Path):
                _styles.append(WebHook.load_style(style, self.encoding))
                continue
            
            raise TypeError(
                f"Styles {get_type_name(new_styles)} contained unexpected type '{get_type_name(new_styles)}',"
                "expected 'Path', 'str', or 'bytes' object."
            )

        self._styles = _styles
    
    @staticmethod
    def requires_window(function):
        """Raises if a method is called without `WebHook.window` being set."""
        def wrapper(self, *args, **kwargs):
            if not self.window:
                raise WebHookError("cannot call '{function.__name__}', the window has not been set.")
            return function(self, *args, **kwargs)
        return wrapper

    @requires_window
    def wrap_function_objects(self):
        """Wraps all functions with `WebHook.Function`"""
        self.functions = [WebHook.Function(function, self.window) for function in self.functions if not hasattr(function, "__webhook__")]
    
    @requires_window
    def wrap_namespace_objects(self):
        """Wraps all `WebHook.Namespace` objects child functions with `WebHook.Function`"""
        for namespace in self.namespaces:
            for key, function in namespace.items():
                if hasattr(function, "__webhook__"):
                    continue
                namespace[key] = WebHook.Function(function, self.window)

    @staticmethod
    def _loads(path, encoding="UTF-8", file_type=None):
        """
        Get the contents of a HTML or CSS file from a `Path` object.
        
        :param path: A `Path` or `str` object of the file to load.
        :param encoding: The encoding to use when reading the file.
        :param file_type: Used for more specific errors.

        :raises TypeError: If the path is not a `Path` or `str` object.
        :raises FileNotFoundError: If the specified path does not exist.
        """

        path = normalize_system_path(path)
        _raise_if_not_path_type(path)

        if not check_path_exists(path):
            raise FileNotFoundError((
                f"Failed to find {file_type} file. ('{path}')", 
                f"Failed to find file. ('{path}')"
            )[file_type is None])
        
        return read_file_contents(path, encoding)
    
    load_html = staticmethod(lambda path, encoding="UTF-8": WebHook._loads(path, encoding, "HTML"))
    load_style = staticmethod(lambda path, encoding="UTF-8": WebHook._loads(path, encoding, "CSS"))