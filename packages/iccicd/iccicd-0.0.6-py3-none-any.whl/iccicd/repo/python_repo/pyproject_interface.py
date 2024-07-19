from pathlib import Path
from typing import Any, cast
import logging
import tomlkit
from tomlkit import TOMLDocument

from iccicd.version import Version

logger = logging.getLogger(__name__)


class PyProjectInterface:
    """
    This class is an interface to the content of a project's
    pyproject.toml file, allowing programmatic access and manipulation.
    """

    def __init__(
        self, repo_path: Path, project_file_name: str = "pyproject.toml"
    ) -> None:
        self.repo_path = repo_path
        self.file_name = project_file_name
        self.doc: dict[str, Any] = {}

    def get_version(self) -> Version:
        if not self.doc:
            self._read_project_file()
        return Version(self.doc["project"]["version"])

    def set_version(self, version: Version):
        if not self.doc:
            self._read_project_file()
        self.doc["project"]["version"] = str(version)
        self._write_project_file()

    def _read_project_file(self):
        pyproject_path = self.repo_path / self.file_name
        with open(pyproject_path, "r") as f:
            content = f.read()
        self.doc = tomlkit.parse(content)

    def _write_project_file(self):
        with open(self.repo_path / self.file_name, "w") as f:
            f.write(tomlkit.dumps(cast("TOMLDocument", self.doc)))
