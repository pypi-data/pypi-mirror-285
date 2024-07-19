from pathlib import Path

from iccicd.version import Version


class Repo:
    def __init__(self, path: Path) -> None:
        self.path = path

    def get_version(self) -> Version:
        return Version()

    def bump_version(self, bump_type: str):
        pass
