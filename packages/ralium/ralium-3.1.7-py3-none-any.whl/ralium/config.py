from ralium.util.common import get_type_name

class WindowConfig:
    """
    A Window Configuration Object.

    :param title: The Window Title.
    :param icon: The Window Icon.
    :param size: The Window Size.
    :param min_size: The minimum size the Window can be.
    :param resizable: If the window can be resized.
    :param use_builtins: Add provided a `Namespace` called `ralium` with a list helpful functions to JavaScript.
    :param kwargs: Extra arguments for the `pywebview.create_window` function.

    :raises TypeError: If a specific config option has an invalid value type.
    """

    def __init__(self,
        title = None,
        icon = None,
        size = (900, 600), 
        min_size = (300, 300), 
        resizable = True,
        use_builtins = True,
        **kwargs
    ):
        self.icon = icon
        self.size = size
        self.title = title
        self.min_size = min_size
        self.use_builtins = use_builtins
        self.is_resizable = resizable
        self.other_options = kwargs

        if not isinstance(title, str) and title is not None:
            raise TypeError(f"Expected the title to be a 'str' object, instead got '{get_type_name(title)}'")
        
        if not isinstance(size, tuple):
            raise TypeError(f"Expected the window size to be a 'tuple' object, instead got '{get_type_name(size)}'")
        
        if len(size) != 2:
            raise TypeError(f"Expected the window size to be a 'tuple' object with a length of 2.")
        
        if not isinstance(min_size, tuple):
            raise TypeError(f"Expected the minimum window size to be a 'tuple' object, instead got '{get_type_name(min_size)}'")
        
        if len(min_size) != 2:
            raise TypeError(f"Expected the minimum window size to be a 'tuple' object, with a length of 2.")

        self.width, self.height = size
        self.min_width, self.min_height = min_size

        if not isinstance(self.width, int):
            raise TypeError(f"Expected the window width to be an 'int' object, instead got '{get_type_name(self.width)}'")
        
        if not isinstance(self.height, int):
            raise TypeError(f"Expected the window height to be an 'int' object, instead got '{get_type_name(self.height)}'")
        
        if not isinstance(self.min_width, int):
            raise TypeError(f"Expected the minimum window width to be an 'int' object, instead got '{get_type_name(self.min_width)}'")
        
        if not isinstance(self.min_height, int):
            raise TypeError(f"Expected the minimum window height to be an 'int' object, instead got '{get_type_name(self.min_height)}'")
        
        if not isinstance(self.is_resizable, bool):
            raise TypeError(f"Expected a 'bool' object for argument 'resizable', instead got '{get_type_name(self.child_window)}'")
    
    def as_webview_kwargs(self):
        """A helper function for converting the configuration options to a dict for the `pywebview.create_window` function."""

        return {
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "min_size": self.min_size,
            "resizable": self.is_resizable
        }