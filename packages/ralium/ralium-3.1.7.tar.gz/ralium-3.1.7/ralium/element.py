from ralium.util.common import get_type_name
from ralium.util.const import (
    ALL_HTML_ELEMENT_INSTANCE_METHODS, 
    RALIUM_ID_IDENTIFIER_PREFIX
)

import uuid

def create_ralium_id(tag):
    """Creates a new ralium ID to a `BeautifulSoup` element."""
    ralium_id = f"{RALIUM_ID_IDENTIFIER_PREFIX}{uuid.uuid1()}"
    tag['class'] = f"{ralium_id} {' '.join(tag.get('class', []))}".strip()
    return ralium_id

def create_soup_element(soup, tag, attrs=None, **props):
    """
    A helper function for creating new `BeautifulSoup` elements.

    :param soup: A `BeautifulSoup` object.
    :param tag: The name of the element to create.
    :param attrs: A `dict` of HTML attributes to add to the new tag.
    :param props: A keyword `dict` of `BeautifulSoup` attributes to set.

    :returns: The newly created tag.
    """

    element = soup.new_tag(tag)
    attrs = attrs or {}

    if not isinstance(attrs, dict):
        raise TypeError(f"Expected element attributes to be of type dict, instead got '{get_type_name(attrs)}'")

    for name, value in props.items():
        setattr(element, name, value)
    
    for name, value in attrs.items():
        element[name] = value

    return element

class JS:
    class _RawStr(str): pass

    @staticmethod
    def str(__value):
        return f'"{__value}"'
    
    @staticmethod
    def raw(__value):
        return JS._RawStr(__value)

    true = str("true")
    false = str("false")

    @staticmethod
    def bool(__value):
        if __value == "true":
            return True

        if __value == "false":
            return False

    class ClassList(list):
        def __init__(self, element):
            self.element = element
            super().__init__(str(element._eval(f"{element._as_js_str()}.classList")).split(' '))
        
        def add(self, classname):
            if classname in self:
                return

            super().append(classname)
            self.element._eval(f'{self.element._as_js_str()}.classList.add("{classname}")')
        
        def remove(self, classname):
            if classname not in self:
                return
            
            super().remove(classname)
            self.element._eval(f'{self.element._as_js_str()}.classList.remove("{classname}")')
    
HTMLElementAttributes = [
    "_ralium_id", 
    "_ralium_window", 
    "classList"
]

class HTMLElement:
    def __init__(self, window, id):
        self._ralium_id = id
        self._ralium_window = window
        self.classList = JS.ClassList(self)

        if RALIUM_ID_IDENTIFIER_PREFIX in self._ralium_id or not id:
            return

        classes = str(self._eval(f""" '' + document.getElementById("{id}").classList;""")).split(' ')

        if RALIUM_ID_IDENTIFIER_PREFIX in classes[0]:
            self._ralium_id = classes[0]
            return

        for classname in classes:
            if RALIUM_ID_IDENTIFIER_PREFIX in classname:
                self._ralium_id = classname
        
    def __getattr__(self, identifier):
        if identifier in ALL_HTML_ELEMENT_INSTANCE_METHODS:
            def wrapper(*args, **kwargs):
                _prepare = lambda v: (str(v), f'"{v}"')[isinstance(v, str)]
                args_str = [_prepare(arg) for arg in args]
                args_str.extend([f'{_prepare(key)}={_prepare(value)}' for key, value in kwargs.items()])
                args_str = ",".join(args_str)

                return self._eval(f"{self._as_js_str()}.{identifier}({args_str})")
            
            wrapper.__name__     = identifier
            wrapper.__qualname__ = f"HTMLElement.{identifier}"

            return wrapper

        return self._parse(self._eval(f"{self._as_js_str()}.{identifier}"))
    
    def __setattr__(self, identifier, value):
        if identifier in HTMLElementAttributes:
            return object.__setattr__(self, identifier, value)
        
        if isinstance(value, str) and not isinstance(value, JS._RawStr):
            value = JS.str(value)

        self._eval(f"{self._get_js_element()}.{identifier} = {value};")
    
    def _get_js_element(self):
        return f"document.getElementsByClassName('{self._ralium_id}')[0]"
    
    def _as_js_str(self):
        return f"'' + {self._get_js_element()}"
    
    def _eval(self, cmd):
        return self._ralium_window.webview.evaluate_js(cmd)
    
    def _parse(self, value):
        if value in ["true", "false"]:
            return JS.bool(value)
        return value