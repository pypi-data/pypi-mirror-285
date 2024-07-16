from ralium.util.common import normalize_webhook_url

class WindowNavigation:
    """
    The Window Navigation Manager.

    :param current_url: The url to initialize with.
    """

    def __init__(self, current_url = "/"):
        self.__previous = None
        self.__location = normalize_webhook_url(current_url)
    
    @property
    def previous(self):
        return self.__previous

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, new_url):
        self.__previous = None
        self.__location = normalize_webhook_url(new_url)