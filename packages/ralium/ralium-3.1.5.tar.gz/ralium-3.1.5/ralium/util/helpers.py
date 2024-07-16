from pathlib import Path

import inspect

__all__ = ["get_type_name", "_force_args_as_path", "_raise_if_not_path_type"]

def get_type_name(object):
    """Returns the name of an objects type."""
    return type(object).__name__

def __patch_argument(value, absolute):
    if isinstance(value, Path):
        if absolute:
            return value.absolute()
        else:
            return value

    if isinstance(value, str):
        if absolute:
            return Path(value).absolute()
        else:
            return Path(value)

    return value

def _force_args_as_path(absolute=True):
    """
    Converts all arguments of type `str` to a `Path` object.
    Already existing `Path` objects are made absolute if the
    argument `absolute` is set to true.
    """

    _absolute = absolute

    def handler(function):
        def wrapper(*args, **kwargs):
            _patched_args = [__patch_argument(arg, _absolute) for arg in args]
            _patched_kwargs = {key: __patch_argument(value, _absolute) for key, value in kwargs.items()}

            return function(*_patched_args, **_patched_kwargs)
        return wrapper
    
    if inspect.isfunction(absolute):
        _absolute = True
        return handler(absolute)

    return handler

def _raise_if_not_path_type(value):
    """Raises a `TypeError` if `value` is not a `Path` or `str` object."""
    if isinstance(value, str):
        return Path(value)

    if not isinstance(value, Path):
        raise TypeError(f"Expected a 'Path' or 'str' object, instead got '{get_type_name(value)}'")