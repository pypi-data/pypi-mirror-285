from ralium.util.common import (
    get_bundled_filesystem,
    normalize_webhook_url,
    get_type_name,
    create_path
)

from ralium.util.models import StrPath
from ralium.util.const import (
    IMAGE_FILE_EXTENSIONS,
    SYS_BUNDLE_ATTRIBUTE
)

from ralium.util.log import logger
from ralium.api import (
    check_project_path,
    check_routes_path
)

from pathlib import Path
from shutil import COPY_BUFSIZE
from http import HTTPStatus

import urllib.parse
import http.server
import importlib
import posixpath
import sys
import os

def reload_ralium():
    """Reloads the all ralium modules."""

    # Get a reference to all modules before reloading them.
    imported_modules = [module for name, module in sys.modules.items() if name.startswith("ralium")]

    for module in imported_modules:
        importlib.reload(module)

# A modified version of http.server.SimpleHTTPRequstHandler
# made compatible with the custom 'FileSystem' class.
class BundledHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f is not None:
            try:
                self.copyfile(f, self.wfile)
            except:
                return

    def send_head(self):
        """
        Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """

        f = None
        path = self.translate_path(self.path)
        ctype = self.guess_type(path)
        # check for trailing "/" which should return 404. See Issue17324
        # The test for this was added in test_httpserver.py
        # However, some OS platforms accept a trailingSlash as a filename
        # See discussion on python-dev and Issue34711 regarding
        # parsing and rejection of filenames with a trailing slash
        if path.endswith("/"):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            f = get_bundled_filesystem().open(path)
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(len(str(f))))
            self.end_headers()
            return f
        except:
            raise
    
    def translate_path(self, path):
        """
        Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """

        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = "\\"
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

    def copyfile(self, fsrc, fdst):
        """A copy function for `File` objects"""
        fdst_write = fdst.write
        while buf := fsrc[:COPY_BUFSIZE]:
            fdst_write(buf)

class File:
    __slots__ = ("relpath", "content",)

    def __init__(self, relpath, content):
        self.relpath = relpath
        self.content = content
    
    def __str__(self):
        return self.content.decode()

    def __repr__(self):
        return f"ralium.bundle.File(relpath='{StrPath(self.relpath).replace('\\', '/')}', content={repr(self.content)})"
    
class Bundle:
    __slots__ = ("url", "page", "server", "styles",)

    def __init__(self, *, url, page, server, styles):
        self.url = url
        self.page = page
        self.server = server
        self.styles = styles
    
    def __repr__(self):
        return f"ralium.bundle.Bundle(url='{self.url}', page={repr(self.page)}, server={repr(self.server)}, styles=[{''.join([repr(v) for v in self.styles])}])"

class FileSystem:
    __slots__ = ("images", "styles", "bundles", "dirs", "files",)

    def __init__(self, *, images, styles, bundles):
        self.images = images
        self.styles = styles
        self.bundles = bundles

        self.dirs = ['/']
        self.files = {}

        for image in images:
            self.__add_file(image)

        for style in styles:
            self.__add_file(style)
        
        for bundle in bundles:
            self.__add_file(bundle.page)

            if bundle.server is not None:
                self.__add_file(bundle.server)
            
            for style in bundle.styles:
                self.__add_file(style)
    
    def __add_file(self, file):
        # Remove the empty string ''
        segments = StrPath(file.relpath).split('/')[1:]
        segments = [StrPath('/', *segments[:i], v) for i, v in enumerate(segments)]

        self.mkdirs(*segments[:-1])
        self.mkfiles(**{segments[-1]: file.content})

    def open(self, filename):
        if isinstance(filename, Path):
            filename = str(filename)
        elif isinstance(filename, bytes):
            filename = filename.decode()

        try:
            return self.files[StrPath(filename)]
        except KeyError:
            raise FileNotFoundError(f"'{filename}' does not exist.")
    
    def exists(self, path):
        path = StrPath(path)
        if self.files.get(path) is not None:
            return False
        return path in self.dirs

    def mkdirs(self, *dirs):
        self.dirs.extend(filter(lambda v: v not in self.dirs, dirs))
    
    def mkfile(self, filename, data):
        if not isinstance(filename, str):
            raise TypeError(f"Expected filename to be a 'str' object, intead got '{get_type_name(filename)}'")
        
        if not isinstance(data, bytes):
            raise TypeError(f"Expected file content to be a 'bytes' object, instead got '{get_type_name(data)}'.")

        self.files[filename] = data
    
    def mkfiles(self, **files):
        for filename, data in files.items():
            self.mkfile(filename, data)

class PyBundler:
    __slots__ = ("pyfile", "project", "routes", "styles", "images",)

    def __init__(self, pyfile, project):
        self.pyfile = pyfile
        self.project = create_path(project)
        self.routes = self.project/"routes"
        self.styles = self.project/"styles"
        self.images = self.project/"images"

        check_project_path(self.project)
        check_routes_path(self.routes)

    def view(self):
        bundles = []
        shared_images = self.collect(self.images, PyBundler.isimage)
        shared_styles = self.collect(self.styles, PyBundler.isstyle)

        for root, _, files in os.walk(self.routes):
            # Ignore empty directories and __pycache__
            if not files or Path(root).name == "__pycache__":
                logger.info(f"skipping '{root}' ({'empty' if not files else '__pycache__'})")
                continue

            url = normalize_webhook_url(root.removeprefix(str(self.routes)))
            page = None
            server = None
            styles = [*shared_styles]

            for file in files:
                path = Path(root, file).absolute()
                relpath = self.relpath(path)
                filename = path.name

                match filename:
                    case "+page.html":
                        page = File(relpath, self.get_content(path))
                    case "+server.py":
                        server = File(relpath, self.get_content(path))
                    case _:
                        if not PyBundler.isstyle(filename): continue
                        styles.append(File(relpath, self.get_content(path)))
                
                logger.info(f"copying '{path}'")
            
            bundles.append(Bundle(url=url, page=page, server=server, styles=styles))
        
        return [
            b"import ralium.bundle\n",
            b"import sys\n",
            f"setattr(sys, '{SYS_BUNDLE_ATTRIBUTE}', ralium.bundle.FileSystem(\n".encode(),
            f"    images = {shared_images},\n".encode(),
            f"    styles = {shared_styles},\n".encode(),
            f"    bundles = {bundles}\n".encode(),
            b"))\n",
            b"ralium.bundle.reload_ralium()\n\n",
            self.get_content(self.pyfile)
        ]
    
    def relpath(self, path):
        return Path(str(path.absolute()).removeprefix(str(self.project.parent)))

    def collect(self, dir, callback):
        data = []

        for root, _, files in os.walk(dir):
            root = Path(root).absolute()

            for file in files:
                path = root / file
                if not callback(path): continue

                logger.info(f"copying '{path}'")
                data.append(File(self.relpath(path), PyBundler.get_content(path)))
        
        return data

    @staticmethod
    def isstyle(filename):
        return Path(filename).suffix == ".css"
    
    @staticmethod
    def isimage(filename):
        return Path(filename).suffix in IMAGE_FILE_EXTENSIONS
    
    @staticmethod
    def get_content(filename):
        if not Path(filename).exists():
            return
        
        if isinstance(filename, Path):
            filename = str(filename)
        
        with open(filename, "rb") as f:
            return f.read()