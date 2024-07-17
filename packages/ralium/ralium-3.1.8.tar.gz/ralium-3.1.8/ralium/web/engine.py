from ralium.util.exceptions import WebBridgeError
from ralium.util.common import get_http_request_handler
from ralium.web.bridge import WebBridge
from ralium.element import HTMLElement

from bs4 import BeautifulSoup

import socketserver
import threading
import os

def process_api_calldata(window, calldata):
    if calldata is None:
        return []

    webhook = window.webhooks.get(window.navigation.location)
    new_calldata = []

    for data in calldata:
        if isinstance(data, dict):
            element_id = data.get("className", None)
            local_name = data.get("localName", None)

            if element_id is None or local_name is None or element_id not in webhook.elements: 
                continue

            soup = BeautifulSoup(window.webview.html, "html.parser")
            element = soup.find(local_name, {"class": element_id})

            new_calldata.append(HTMLElement(window, element_id, element))
            continue

        new_calldata.append(data)
    
    return new_calldata

class WebEngine:
    def __init__(self, window):
        self.port, worker = self.initialize_tcp_server()
        
        self._thread = threading.Thread(target=worker, daemon=True)
        self._running = threading.Event()

        self.bridge = WebBridge()
        self.functions = WebBridge.Collection()

        # Strictly for the 'WebviewApi' class created by 'WebEngine.create_webview_api'
        self._window = window

        self.start = self._thread.start

    def __str__(self):
        return f"http://localhost:{self.port}/"

    @property
    def running(self):
        return not self._running.is_set()
    
    def close(self):
        self._running.set()
        self._thread.join(timeout=5)
    
    def create_webview_api(engine):
        class WebviewApi:
            def __init__(self):
                return
            
            # https://github.com/r0x0r/pywebview/issues/1405
            def bridge(self, object, calldata=None):
                if not engine.functions.get(object, False): 
                    return

                calldata = process_api_calldata(engine._window, calldata)

                if calldata:
                    return engine.functions[object](*calldata)
                
                return engine.functions[object]()
        
        return WebviewApi()
    
    def initialize_tcp_server(self):
        httpd = socketserver.TCPServer(("", 0,), get_http_request_handler())
        port = httpd.socket.getsockname()[1]

        def worker():
            while self.running:
                httpd.handle_request()
            os._exit(0)
        
        return port, worker