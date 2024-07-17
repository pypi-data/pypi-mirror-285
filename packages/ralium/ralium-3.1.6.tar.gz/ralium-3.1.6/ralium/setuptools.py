from PyInstaller.__main__ import run as create_executable

from ralium.util.exceptions import SetupError
from ralium.util.common import check_bundled, get_type_name
from ralium.util.const import FILE_EXTENSIONS
from ralium.util.log import logger
from ralium.bundle import PyBundler
from ralium.util import __version__

from pathlib import Path
import subprocess
import mycompat
import sys
import os

def __create_exe_str_error(name, var):
    return TypeError(f"Expected executable {name} to be of type 'str', instead got '{get_type_name(var)}'")

def __create_add_data_arg(src, dst):
    return f'--add-data={src}{os.pathsep}{dst}'

def collect_project(project):
    """
    Collects all necessary files from a Ralium Project used within the executable main Python file.

    :param project: The path to the project folder.
    
    :returns: A `dict` where the keys contain the absolute paths and the values represent the relative paths.
    """

    files = {}
    project = Path(project).absolute()
    routes = project/"routes"
    styles = project/"styles"
    images = project/"images"
    
    if os.path.exists(routes):
        for root, _, files in os.walk(routes):
            dest = Path(project.name, root.removeprefix(str(project)))
            files.update({str(Path(root, file).absolute()): dest for file in files if Path(file).suffix in FILE_EXTENSIONS})
    
    if os.path.exists(styles):
        for root, _, files in os.walk(styles):
            dest = Path(project.name, root.removeprefix(str(project)))
            files.update({str(Path(root, file).absolute()): dest for file in files if Path(file).suffix == ".css"})
    
    if os.path.exists(images):
        for root, _, files in os.walk(images):
            dest = Path(project.name, root.removeprefix(str(project)))
            files.update({str(Path(root, file).absolute()): dest for file in files})
    
    return files

def bundle(
    pyfile,
    project,
    filename = None,
    distpath = None
):
    """
    Bundles a Ralium project to a single python file.

    :param pyfile: The python file to compile.
    :param project: The path to the project directory.
    :param filename: The name to set for the bundled file.
    :param distpath: The directory to create the bundle in. (Default: `dist`)
    
    :returns: The path to the bundled file created.

    :raises TypeError: If the incorrect types are provided for certain arguments.
    :raises SetupError: If `project` is None.
    :raises FileNotFoundError: If the `pyfile` or the `project` path does not exist.
    """

    if project is None:
        raise SetupError("Cannot bundle project without a project directory.")

    distpath = Path(distpath or "dist").absolute()

    if not os.path.exists(distpath):
        os.mkdir(distpath)
        logger.info("created %s", distpath)

    base, ext = os.path.splitext(os.path.basename(pyfile))
    filename = os.path.join(distpath, f"{filename or base}.bundle{ext}")

    logger.info("Bundling '%s' with project '%s'", pyfile, os.path.abspath(project))

    code = PyBundler(pyfile, project).view()

    # PyInstaller 6.6.0 and greater require these modules on Windows.
    # If you compile the program without these lines added to the file.
    # An ImportError will occur in which the pywin32-ctypes module needs to be installed.
    # Adding these lines as imports before everything else fixes this problem.
    if mycompat.is_win:
        code.insert(0, b"from win32ctypes.pywin32 import pywintypes\n")
        code.insert(1, b"from win32ctypes.pywin32 import win32api\n")

    with open(filename, "wb") as f:
        f.writelines(code)

    logger.info("wrote %s", filename)
    logger.info("Finished Bundling")

    return os.path.abspath(filename)

def setup(
    pyfile,
    name = None,
    icon = None,
    bundle = False,
    project = None,
    onefile = True,
    noconsole = True,
    bundle_dist = None,
    optimize = None,
    pyi_args = None,
    use_subprocess = False,
):
    """
    Compiles a Ralium project to an executable using PyInstaller.

    :param pyfile: The python file to compile.
    :param name: Display name for the executable.
    :param icon: Display icon for the executable.
    :param bundle: Bundles all of the HTML, CSS, python and image files into one executable. (Requires a project directory)
    :param project: Directory of the project.
    :param onefile: Creates the executable as a standalone file.
    :param noconsole: Prevents a console from being displayed.
    :param bundle_dist: The directory name Ralium will use for bundling projects. (Default: `dist`)
    :param optimize: Set the `PYTHONOPTIMIZE` level or the PyInstaller `--optimize` flag. (Default: `0`)
    :param pyi_args: Extra parameters for PyInstaller to use.
    :param use_subprocess: Use `PyInstaller` through a subprocess.

    :raises TypeError: If the name or icon is not a `str` or `None`.
    :raises SetupError: If `bundle` is True while the `project` directory is None or does not exist.
    :raises RuntimeError: If this function is called within an already compiled executable file.
    :raises FileNotFoundError: If a certain file path doesn't exist.
    """

    if not isinstance(pyfile, (Path, str, bytes,)):
        raise TypeError(f"Expected 'pyfile' to be a 'Path', 'str', or 'bytes' object, instead got '{get_type_name(pyfile)}'")

    logger.info("Ralium: %s", __version__)

    if mycompat.is_frozen:
        raise RuntimeError("Ralium 'setup' cannot be ran from an executable file.")
    elif check_bundled():
        raise RuntimeError("Ralium 'setup' cannot be ran from a bundled file.")

    if not Path(pyfile).exists():
        raise FileNotFoundError(f"Failed to find python file '{pyfile}'")
    
    if optimize not in [None, *range(0, 3)]:
        raise ValueError("The optimization level must be the value of 0, 1, or 2.")

    args = [pyfile, *(pyi_args or [])]

    if name is not None:
        if not isinstance(name, str):
            raise __create_exe_str_error("name", name)
        
        args.append(f"--name={name}")
    
    if icon is not None:
        if not isinstance(icon, str):
            raise __create_exe_str_error("icon", icon)

        if not os.path.exists(icon):
            raise FileNotFoundError(f"Failed to find icon file with path: '{icon}'")
        
        args.append(f"--icon={icon}")
    
    if onefile:
        args.append(f"--onefile")
    
    if noconsole:
        args.append(f"--noconsole")
    
    if bundle:
        args[0] = globals()["bundle"](
            pyfile=pyfile, 
            project=project,
            name=name,
            distpath=bundle_dist
        )
    elif project:
        for src, dst in collect_project(project).items():
            args.append(__create_add_data_arg(src, dst))

    if use_subprocess:
        optimize_flag = ""

        match optimize:
            case 1: optimize_flag = "-O"
            case 2: optimize_flag = "-OO"
        
        args = [
            sys.executable,
            "-m",
            "PyInstaller",
            *args
        ]

        if optimize_flag:
            args.insert(1, optimize_flag)
        
        return subprocess.run(args) and None
    else:
        args.append(f"--optimize={optimize or 0}")
    
    create_executable(args)