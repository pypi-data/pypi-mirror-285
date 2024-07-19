import logging
import os
from pathlib import Path

from iccore import process
from iccicd.version import Version

logger = logging.getLogger(__name__)


class GitUser:
    def __init__(self, name: str = "", email: str = "") -> None:
        self.name = name
        self.email = email

    def is_set(self):
        return self.name and self.email


class GitRemote:
    def __init__(self, name: str = "origin", url=""):
        self.url = url
        self.name = name


class GitRepo:
    """
    Representation of a git repository, including methods for querying and modifying
    repo contents.
    """

    def __init__(self, path: Path, read_user: bool = True) -> None:
        self.path = path

        if read_user:
            email, name = self._read_user()
            self.user: GitUser = GitUser(email, name)
        else:
            self.user = GitUser()

        self.remotes: list[GitRemote] = []
        self._read_remotes()

    def add_remote(self, remote: GitRemote):
        logger.info("Adding remote with name %s and url %s", remote.name, remote.url)
        cmd = f"git remote add {remote.name} {remote.url}"
        process.run(cmd, self.path)
        self.remotes.append(remote)

    def _read_user(self):
        email = self.get_user_email()
        name = self.get_user_name()
        return email, name

    def set_user(self, user: GitUser):
        self.user = user
        logger.info(
            "Setting user name: %s and email: %s", self.user.email, self.user.name
        )
        self.set_user_email(self.user.email)
        self.set_user_name(self.user.name)

    def add_all(self):
        cmd = "git add ."
        process.run(cmd, self.path)

    def commit(self, message: str):
        cmd = f"git commit -m {message}"
        process.run(cmd, self.path)

    def push(
        self,
        remote: str = "origin",
        src: str = "HEAD",
        dst: str = "main",
        extra_args: str = "",
    ):
        cmd = f"git push {remote} {src}:{dst} {extra_args}"
        process.run(cmd, self.path)

    def push_tags(self, remote: str = "origin"):
        cmd = f"git push --tags {remote}"
        process.run(cmd, self.path)

    def set_tag(self, tag: str):
        cmd = f"git tag {tag}"
        process.run(cmd, self.path)

    def set_user_email(self, email: str):
        cmd = f"git config user.email {email}"
        process.run(cmd, self.path)

    def set_user_name(self, name: str):
        cmd = f"git config user.name {name}"
        process.run(cmd, self.path)

    def has_tags(self) -> bool:
        cmd = "git tag -l"
        # Result will be empty string if no tags
        return bool(process.run(cmd, self.path, is_read_only=True))

    def _read_remotes(self):
        cmd = "git remote"
        remote_names = process.run(cmd, is_read_only=True).splitlines()
        for name in remote_names:
            self.remotes.append(GitRemote(name=name))

    def get_user_email(self) -> str:
        cmd = "git config user.email"
        return process.run(cmd, self.path, is_read_only=True)

    def get_user_name(self) -> str:
        cmd = "git config user.name"
        return process.run(cmd, self.path, is_read_only=True)

    def get_latest_tag_on_branch(self) -> str:
        if not self.has_tags():
            return ""

        cmd = "git describe --tags --abbrev=0"
        return process.run(cmd, self.path, is_read_only=True)

    def get_branch(self) -> str:
        cmd = "git branch --show-current"
        return process.run(cmd, self.path, is_read_only=True)

    def switch_branch(self, target_branch: str):
        cmd = f"git checkout {target_branch}"
        return process.run(cmd, self.path)

    def increment_tag(
        self,
        version_scheme: str = "semver",
        field: str = "patch",
        branch="main",
        remote: str | None = None,
    ):

        current_branch = self.get_branch()
        if current_branch != branch:
            self.switch_branch(branch)

        latest_tag = self.get_latest_tag_on_branch()
        version = Version(latest_tag, version_scheme)
        logging.info("Current tag is: %s", version)

        version.increment(field)
        logging.info("Updating tag to: %s", version)
        self.set_tag(str(version))

        if remote:
            working_remote = remote
        else:
            working_remote = self.remotes[-1].name
        logging.info("Setting remote to: %s", working_remote)
        self.push_tags(working_remote)


if __name__ == "__main__":

    # A little info dump, maybe useful for testing or sanity checking

    repo = GitRepo(Path(os.getcwd()))

    print("Has remotes:")
    for remote in repo.remotes:
        print(remote.name)

    print("On branch:")
    print(repo.get_branch())
