import inspect
import logging

# Same logger format as PyInstaller.
# https://github.com/pyinstaller/pyinstaller/blob/develop/PyInstaller/log.py#L35
FORMAT = '%(relativeCreated)d %(levelname)s: %(message)s'

logging.basicConfig(format=FORMAT, level=logging.INFO)

class BasicLogger:
    def __init__(self):
        logger = logging.getLogger("Ralium")
        members = inspect.getmembers(logger, predicate=inspect.ismethod)

        self.disabled = False
        self._methods = []

        for name, method in members:
            self._methods.append(name)
            super().__setattr__(name, method)
    
    def __getattribute__(self, name):
        _methods = super().__getattribute__("_methods")
        disabled = super().__getattribute__("disabled")

        if name in _methods and disabled:
            return lambda *_, **__: None
        
        return super().__getattribute__(name)
    
    def enable(self):
        self.disabled = False
    
    def disable(self):
        self.disabled = True

logger = BasicLogger()
enableLogging = logger.enable
disableLogging = logger.disable