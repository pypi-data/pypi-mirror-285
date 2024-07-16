# Regex pattern for match single line HTML tags used by `PyHtml`
RE_HTML_PATTERN = r"((<.*>.*</.*>)|(<.*/>))"

# Supported HTML file extensions that `setup` looks for
HTML_FILE_EXTENSIONS = [".htm", ".html"]

# All file extensions that `setup` looks for
FILE_EXTENSIONS = [*HTML_FILE_EXTENSIONS, ".css", ".py"]

# Used for backwards compatibility with Python versions below 3.12. Older versions 
# raise a SyntaxError when you try to include a plain backslash in an f-string, like: f"{'\\'}". 
# Using a constant instead, like: f"{BACKSLASH}" circumvents this problem.
BACKSLASH = "\\"

# This is stored as a constant to make it easy to change in the future. (If Needed)
SYS_BUNDLE_ATTRIBUTE = "bundled"

# Basic HTML Template, used as a fallback for `pywebview`
HTML_TEMPLATE = """<!DOCTYPE html><html><head lang="en"><meta charset="UTF-8"></head><body></body></html>"""

# Supported Image Extensions
IMAGE_FILE_EXTENSIONS = [
    ".apng", ".gif", ".ico", ".cur", ".jpg", ".jpeg", ".webp",
    ".jfif", ".pjpeg", ".pjp", ".png", ".svg", ".icns", ".ico"
]

# The name the ralium api uses for storing exposed functions
RALIUM_API_REGISTRY_IDENTIFIER = "__ralium_registry__"

# The prefix used for creating ralium element ids
RALIUM_ID_IDENTIFIER_PREFIX = "ralium-"

# A list of all HTML Elements
ALL_HTML_ELEMENTS = [
    "a", "abbr", "acronym", "address", "area", "article", "aside", "audio", "b", "base",
    "bdi", "bdo", "big", "blockquote", "body", "br", "button", "canvas", "caption", "center",
    "cite", "code", "col", "colgroup", "data", "datalist", "dd", "del", "details", "dfn", "dialog",
    "dir", "div", "dl", "dt", "em", "embed", "fencedframe", "fieldset", "figcaption", "figure",
    "font", "footer", "form", "frame", "frameset", "h1", "head", "header", "hgroup", "hr", "html",
    "i", "iframe", "img", "input", "ins", "kbd", "label", "legend", "li", "link", "main", "map",
    "mark", "marquee", "menu", "menuitem", "meta", "meter", "nav", "nobr", "noembed", "noframes",
    "noscript", "object", "ol", "optgroup", "option", "output", "p", "param", "picture", "plaintext",
    "portal", "pre", "progress", "q", "rb", "rp", "rt", "rtc", "ruby", "s", "samp", "script", "search",
    "section", "select", "slot", "small", "source", "span", "strike", "strong", "style", "sub", "summary",
    "sup", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr",
    "track", "tt", "u", "ul", "var", "video", "wbr", "xmp"
]

# A list of all methods attached to elements
ALL_HTML_ELEMENT_INSTANCE_METHODS = [
    "after", "animate", "append", "attachShadow", "before", "checkVisibility", "closest",
    "computedStyleMap", "getAnimations", "getAttribute", "getAttributeNames", "getAttributeNode",
    "getAttributeNodeNS", "getAttributeNS", "getBoundingClientRect", "getClientRects",
    "getElementsByClassName", "getElementsByTagName", "getElementsByTagNameNS", "getHTML",
    "hasAttribute", "hasAttributeNS", "hasAttributes", "hasPointerCapture", "insertAdjacentElement",
    "insertAdjacentHTML", "insertAdjacentText", "matches", "prepend", "querySelector",
    "querySelectorAll", "releasePointerCapture", "remove", "removeAttribute", "removeAttributeNode",
    "removeAttributeNS", "replaceChildren", "replaceWith", "requestFullscreen", "requestPointerLock",
    "scroll", "scrollBy", "scrollIntoView", "scrollIntoViewIfNeeded", "scrollTo", "setAttribute",
    "setAttributeNode", "setAttributeNodeNS", "setAttributeNS", "setCapture", "setHTML",
    "setPointerCapture", "toggleAttribute"
]