from pathlib import Path

class StrPath(str):
    """A helper class for creating a `Path` object as a `str` object."""
    def __new__(cls, *args):
        return str(Path(*args)).replace('\\', '/')

class NamedDict(dict):
    def __init__(self, iterable = None):
        for key, value in (iterable or {}).items():
            if isinstance(value, dict):
                self[key] = NamedDict(value)
                continue

            self[key] = value
    
    def __getattr__(self, name):
        if not super().__contains__(name):
            raise AttributeError(f"Object does not contain value '{name}'")
        return super().__getitem__(name)

class NestedNamedDict(NamedDict):
    def __getattr__(self, name, value):
        if not super().__contains__(name):
            super()[name] = NestedNamedDict()
        return super().__getitem__(name, value)