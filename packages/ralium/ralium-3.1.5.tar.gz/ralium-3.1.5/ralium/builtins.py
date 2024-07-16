from ralium.element import JS
import webbrowser

__registry__ = []

def builtin(function):
    if function not in __registry__:
        __registry__.append(function)
    
    return function

@builtin
def refresh(window):
    window.display(window.navigation.location)

@builtin
def redirect(window, url):
    window.display(url)

@builtin
def shutdown(window):
    window.shutdown()

@builtin
def getUrl(window, element = None):
    element.innerHTML = JS.str(window.navigation.location)
    return window.navigation.location

@builtin
def getServerPort(window, element = None):
    element.innerHTML = window.engine.port
    return window.engine.port

@builtin
def openBrowserTab(window, path):
    return webbrowser.open_new_tab(path)