from ralium.util.common import is_function
from ralium.web.webhook import WebHook

class WebBridge:
    class Collection(dict):
        def add(self, function):
            self[str(function)] = function

    def __init__(self, *functions):
        self.bridges = []

        for function in functions:
            self.new(function)
        
        self.clear = self.bridges.clear
    
    def __str__(self):
        return "".join(self.bridges)
    
    def create_javascript_function(self, name, string):
        return f"function {name}(...calldata){{return pywebview.api.bridge(\"{string}\", calldata)}}"

    def create_javascript_namespace(self, alias, *functions, **named_functions):
        functions = [
            f'{function.__name__}: {self.create_javascript_function("", str(function))}'
            for function in functions
        ]

        functions.extend([
            f'{alias}: {self.create_javascript_function("", str(function))}'
            for alias, function in named_functions.items()
        ])

        return f"let {alias} = {{{','.join(functions)}}};"

    def new(self, obj):
        if is_function(obj):
            return self.bridges.append(self.create_javascript_function(obj.__name__, str(obj)))
        
        if isinstance(obj, WebHook.Namespace):
            return self.bridges.append(self.create_javascript_namespace(obj.alias, **dict(obj.items())))