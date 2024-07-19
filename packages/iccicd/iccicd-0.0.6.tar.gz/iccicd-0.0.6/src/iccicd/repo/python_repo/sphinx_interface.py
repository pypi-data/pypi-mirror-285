from pathlib import Path

from iccicd.version import Version


class SphinxInterface:
    def __init__(self, repo_path: Path, conf_path: Path = Path("docs/conf.py")) -> None:
        self.repo_path = repo_path
        self.conf_path = conf_path

    def set_version(self, version: Version):
        conf_path = self.repo_path / self.conf_path
        with open(conf_path, "r") as f:
            lines = f.readlines()

        with open(conf_path, "w") as f:
            for line in lines:
                if "release" in line:
                    line = f"release = '{version}'"
                f.write(line)

    def get_version(self) -> Version:
        conf_path = self.repo_path / self.conf_path
        with open(conf_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            if "release" in line:
                _, val = line.split("=")
                return Version(val.strip().replace("'", ""))
        raise RuntimeError("release key not found in config")
