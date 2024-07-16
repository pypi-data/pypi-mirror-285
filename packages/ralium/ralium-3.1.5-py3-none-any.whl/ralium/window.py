from ralium.util.exceptions import WindowRuntimeError
from ralium.util.listener import ClassListener
from ralium.util.common import get_type_name

from ralium.web.webhook import WebHook, create_namespace
from ralium.web.engine import WebEngine

from ralium.navigation import WindowNavigation
from ralium.config import WindowConfig
from ralium.pyhtml import PyHTML
import ralium.builtins

from ralium.util.const import (
    RALIUM_ID_IDENTIFIER_PREFIX,
    HTML_TEMPLATE
)

from ralium.element import (
    create_soup_element, 
    create_ralium_id,
    HTMLElement
)

from bs4 import BeautifulSoup

import webview

@ClassListener
class Window:
    """
    Represents a Ralium GUI Window.

    :param webhooks: A list of WebHooks that handle each URL.
    :param config: Optional configuration for the window.
    """

    def __init__(self, webhooks, config=None):
        self.data = {}
        self.config = config or WindowConfig()
        self.engine = WebEngine(self)
        self.running = False
        self.webhooks = WebHook.Collection(*webhooks)
        self.navigation = WindowNavigation()

        self.webview = webview.create_window(
            html=HTML_TEMPLATE,
            hidden=True,
            js_api=self.engine.create_webview_api(),
            **self.config.as_webview_kwargs(),
            **self.config.other_options
        )

        __builtins = create_namespace("ralium", *ralium.builtins.__registry__)

        for webhook in webhooks:
            if self.config.use_builtins:
                webhook.namespaces.append(__builtins)

            webhook.window = self
            webhook.wrap_function_objects()
            webhook.wrap_namespace_objects()
        
        self.engine.start()
    
    def getElementsByClassName(self, className):
        """
        Gets all elements with a specific Class Name.

        :param className: The HTML Class to look for.

        :returns: A list of `HTMLElement` Objects. Returns an empty list if no elements are found.

        :raises WindowRuntimeError: If you call this method before starting the `Window`.
        """

        if not self.running:
            raise WindowRuntimeError("Window must be running before calling the 'getElementsByClassName' method.")

        element_classes = self.webview.evaluate_js(f"Array.from(document.getElementsByClassName('{className}')).map((e) => e.classList);")
        return [HTMLElement(self, classList[0]) for classList in element_classes]
    
    def getElementById(self, id):
        """
        Gets an element with a specific Id.

        :param id: The HTML element Id.
        
        :returns: `HTMLElement` object if found or `None`.
        """

        if self.running:
            element_ralium_id = str(self.webview.evaluate_js(f""" '' + document.getElementById("{id}").classList;"""))
            
            classes = element_ralium_id.split(' ')
            ralium_id = classes[0]

            if ralium_id not in RALIUM_ID_IDENTIFIER_PREFIX:
                for classname in classes:
                    if RALIUM_ID_IDENTIFIER_PREFIX in classname:
                        ralium_id = classname
                        break

            if ralium_id == "null":
                return

            return HTMLElement(self, ralium_id)

        soup = BeautifulSoup(self.webview.html, features="lxml")

        element = soup.select(f'#{id}')
        
        if not element:
            return
        
        ralium_id = element[0].get('class')[0]
        return HTMLElement(self, ralium_id)
    
    def load_handler(self, window):
        def on_load():
            window.show()
            window.events.loaded -= on_load

        window.events.loaded += on_load
        
    def display(self, url):
        """
        Displays a URL by calling the WebHook attached to the URL.

        :param url: The URL to display.
        """

        if not isinstance(url, str):
            raise TypeError(f"Expected 'url' argumnet to be a 'str' object, instead got '{get_type_name(url)}'")

        self.navigation.location = url
        webhook = self.webhooks.get(self.navigation.location)

        self.engine.bridge.clear()
        self.engine.functions.clear()

        for function in webhook.functions:
            self.engine.bridge.new(function)
            self.engine.functions.add(function)
        
        for namespace in webhook.namespaces:
            self.engine.bridge.new(namespace)

            for function in namespace.values():
                self.engine.functions.add(function)
        
        html = BeautifulSoup(PyHTML(self, webhook).compile(), features="lxml")
        webhook.elements = [create_ralium_id(element) for element in html.body.find_all()]

        html.body.extend([
            create_soup_element(html, "base",   {"href": str(self.engine)}),
            create_soup_element(html, "script", string=str(self.engine.bridge)),
            create_soup_element(html, "style",  string="\n".join(webhook.styles))
        ])

        self.render(html)

    def render(self, html):
        """Write HTML to the DOM."""
        if not self.running:
            self.webview.html = str(html)
            return

        self.webview.load_html(str(html))
    
    def start(self):
        """Starts the Ralium Window and officially displays the GUI."""
        if self.running: return
        
        self.running = True
        webview.start(self.load_handler, self.webview, private_mode=False)
    
    def show(self):
        """Show a Ralium Window."""
        self.webview.show()
    
    def hide(self):
        """Hide a Ralium Window."""
        self.webview.hide()
    
    def shutdown(self):
        """Shutdown a Ralium Window."""
        self.webview.destroy()
        self.engine.close()