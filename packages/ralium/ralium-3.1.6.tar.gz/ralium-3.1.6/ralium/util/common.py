from ralium.util.helpers import *
from ralium.util.models import StrPath
from ralium.util.const import *

from pathlib import Path

import mycompat
import inspect
import sys
import os

def get_bundled_filesystem():
    """Returns the bundled filesystem or None."""
    return getattr(sys, SYS_BUNDLE_ATTRIBUTE, None)

def check_bundled():
    """Helper function for checking if the project is bundled."""
    return get_bundled_filesystem() is not None

if check_bundled():
    def get_http_request_handler():
        """Returns a HTTP Server Handler."""
        import ralium.bundle
        return ralium.bundle.BundledHTTPRequestHandler
    
    def check_path_exists(path):
        """Helper function for checking if a path exists."""
        path = normalize_system_path(path)
        _raise_if_not_path_type(path)

        return get_bundled_filesystem().exists(path)
    
    def check_path_is_dir(path):
        """Helper function for checking if a path is a directory."""
        path = normalize_system_path(path)
        _raise_if_not_path_type(path)

        return StrPath(path) in get_bundled_filesystem().dirs
    
    def read_file_contents(path, encoding="UTF-8"):
        """Helper function for reading files."""
        path = normalize_system_path(path)
        _raise_if_not_path_type(path)
        
        return get_bundled_filesystem().open(path).decode(encoding)
    
    @_force_args_as_path(absolute=False)
    def create_path(path):
        """
        Helper function for getting file paths.
        If frozen it joins the path with `sys._MEIPASS`.
        Otherwise it just returns the normalized path.
        """
        _raise_if_not_path_type(path)
        return normalize_system_path(path)
else:
    import http.server

    def get_http_request_handler():
        """Returns a HTTP Server Handler."""
        return http.server.SimpleHTTPRequestHandler

    def check_path_exists(path):
        """Helper function for checking if a path exists."""
        path = normalize_system_path(path)
        _raise_if_not_path_type(path)

        return path.exists()
    
    def check_path_is_dir(path):
        """Helper function for checking if a path is a directory."""
        path = normalize_system_path(path)
        _raise_if_not_path_type(path)

        return path.is_dir()
    
    def read_file_contents(path, encoding="UTF-8"):
        """Helper function for reading files."""
        path = normalize_system_path(path)
        _raise_if_not_path_type(path)

        with open(str(path), "r", encoding=encoding) as fp:
            return fp.read()
    
    @_force_args_as_path
    def create_path(path):
        """
        Helper function for getting file paths.
        If frozen it joins the path with `sys._MEIPASS`.
        Otherwise it just returns the normalized path.
        """
        _raise_if_not_path_type(path)

        if mycompat.is_frozen:
            return Path(sys._MEIPASS, path).absolute()

        return path.absolute()

def normalize_webhook_url(path):
    """Normalizes WebHook URL's"""
    return os.path.normpath(f"/{path.lstrip(f'/{BACKSLASH}')}").replace('\\', "/")

@_force_args_as_path(absolute=False)
def normalize_system_path(path):
    """Normalizes System Paths"""
    _raise_if_not_path_type(path)
    
    # Relative paths need to start with a '/' or '\' for windows systems, 
    # this to make bundled projects to work.
    if not path.is_absolute():
        return Path('/' + StrPath(path).lstrip('/'))
    
    return path # pathlib.Path automatically normalizes paths.

is_method = inspect.ismethod
is_function = inspect.isfunction