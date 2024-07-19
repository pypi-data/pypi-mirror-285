import platform
from multiprocessing import cpu_count
import socket
import importlib
from typing import Optional, List, Union
import clisync
import inspect
import types
import sys
from pyhectiqlab.project import Project
from pyhectiqlab.decorators import functional_alias

from pyhectiqlab.logging import hectiqlab_logger as logger

try:
    from git import Repo
except ImportError:
    pass

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata


class PackageVersion:

    @staticmethod
    @functional_alias("get_package_version")
    @clisync.include()
    def all(repos: Union[str, List[str], None] = None) -> dict:
        """Get all packages and system information.

        Args:
            repos (Union[str, List[str], None], optional): List of repositories to get information from. Default: None.

        Returns:
            dict: Dictionary containing Python version, system information, package versions and git repository information.

        Raises:
            logger.error: If an error occurs while getting Python version, system information, package versions or git repository information,
                it logs the error and continue."""
        packages = {}
        try:
            packages["python"] = PackageVersion.python_version()
        except Exception as e:
            logger.error(f"An error occurred while getting Python version: {e}")
        try:
            packages["system"] = PackageVersion.sysinfo()
        except Exception as e:
            logger.error(f"An error occurred while getting system information: {e}")
        try:
            packages["packages"] = PackageVersion.imported_modules_versions()
        except Exception as e:
            logger.error(f"An error occurred while getting package versions: {e}")
        try:
            repos = repos or Project.repos()
            if isinstance(repos, str):
                repos = [repos]

            if repos:
                packages["repos"] = {}
                for repo in repos:
                    packages["repos"][repo] = PackageVersion.repo(repo)
        except Exception as e:
            logger.error(f"An error occurred while getting git repository information: {e}")
        logger.debug(f"Package versions: {packages}")
        return packages

    @staticmethod
    def python_version():
        """Get Python version."""
        return {"Python implementation": platform.python_implementation(), "Python version": platform.python_version()}

    @staticmethod
    def sysinfo():
        """Get system information."""
        return {
            "Compiler": platform.python_compiler(),
            "OS": platform.system(),
            "Release": platform.release(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "CPU cores": cpu_count(),
            "Architecture": platform.architecture()[0],
            "Hostname": socket.gethostname(),
        }

    @staticmethod
    def repo(package_name: str):
        """Get git repository information of a package."""
        repo = PackageVersion._get_repo(package_name)
        if repo is None:
            return
        diff_files = None
        try:
            has_diff = repo.is_dirty()
            if has_diff:
                diff_files = repo.git.diff("--name-only").split("\n")
        except:
            has_diff = "Unknown"

        return {
            "branch": repo.active_branch.name,
            "commit": repo.active_branch.commit.hexsha,
            "remote": repo.remotes.origin.url,
            "has_diff": has_diff,
            "diff_files": diff_files,
        }

    @staticmethod
    def is_dirty(package_name: Optional[str] = None) -> bool:
        """Indicates if the package is dirty."""
        package_name = package_name or Project.repos()

        if package_name is None:
            return False
        if isinstance(package_name, str):
            package_name = [package_name]
        for n in package_name:
            repo = PackageVersion._get_repo(n)
            if repo is None:
                continue
            try:
                if repo.is_dirty():
                    return True
            except:
                continue
        return False

    @staticmethod
    def _get_repo(package_name: str):
        """Get the git repository of a package.

        Args:
            package_name (str): Name of the package.
        """
        try:
            spec = importlib.util.find_spec(package_name)
        except:
            return
        if spec is None:
            return

        path = spec.origin
        try:
            repo = Repo(path, search_parent_directories=True)
        except:
            return

        return repo

    @staticmethod
    def imported_modules_versions():
        global_namespaces = sys.modules
        to_print = {}
        modules = {
            val.__name__.split(".")[0] for _, val in global_namespaces.items() if isinstance(val, types.ModuleType)
        }
        submodules = {
            inspect.getmodule(val).__name__.split(".")[0]
            for _, val in global_namespaces.items()
            if (inspect.getmodule(val) is not None)
        }
        modules = set.union(submodules, modules)

        modules.discard("builtins")
        modules.discard("IPython")
        modules.discard("__main__")

        for module in modules:
            if module.startswith("_"):
                continue
            pkg_version = PackageVersion.module_version(module)
            if pkg_version not in ("not installed", "unknown"):
                to_print[module] = pkg_version

        # Sort keys
        to_print = dict(sorted(to_print.items()))
        return to_print

    @staticmethod
    def module_version(module) -> str:
        """Return the version of a given package"""
        if module == "scikit-learn":
            module = "sklearn"
        try:
            imported = importlib.import_module(module)
        except ImportError:
            version = "not installed"
        else:
            try:
                version = importlib_metadata.version(module)
            except importlib_metadata.PackageNotFoundError:
                try:
                    version = imported.__version__
                except AttributeError:
                    try:
                        version = imported.version
                    except AttributeError:
                        try:
                            version = imported.version_info
                        except AttributeError:
                            version = "unknown"
        if type(version) == bytes:
            version = version.decode("utf-8")
        if type(version) == tuple:
            version = ".".join(map(str, version))
        if type(version) in [float, int]:
            version = str(version)
        return version
