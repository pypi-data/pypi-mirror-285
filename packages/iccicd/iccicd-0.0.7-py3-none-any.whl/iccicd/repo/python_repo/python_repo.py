from pathlib import Path
import logging

from iccicd.repo import Repo
from iccicd.version import Version

from .pyproject_interface import PyProjectInterface
from .sphinx_interface import SphinxInterface

logger = logging.getLogger(__name__)


class PythonRepo(Repo):
    """
    This class represents a Python repository, abstracting
    lower level interfaces to Python project tools like
    'pyproject.toml' and Sphinx config, that don't
    necessarily talk to each other.

    Args:
        path (Path): Path to the repository
    """

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.sphinx = SphinxInterface(self.path)
        self.pyproject = PyProjectInterface(self.path)

    def get_version(self) -> Version:
        return self.pyproject.get_version()

    def increment_version(self, field: str):
        version = self.pyproject.get_version()
        logging.info("Incrementing project version from %s", version)
        version.increment(field)
        self.pyproject.set_version(version)
        self.sphinx.set_version(version)
        logging.info("Incremented project version to %s", version)

    def set_version(self, version: Version):
        logging.info("Setting project version to %s", version)
        self.pyproject.set_version(version)
        self.sphinx.set_version(version)
