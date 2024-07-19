from pathlib import Path
from .git_repo import GitRepo, GitRemote, GitUser


class GitlabProject:
    def __init__(self, instance_url: str, repo_url: str) -> None:
        self.instance_url = instance_url
        self.repo_url = repo_url

    def _get_project_url(self):
        return f"{self.project.instance_url}/{self.repo_url}"

    url = property(_get_project_url)


class GitlabInterface:
    def __init__(
        self, project: GitlabProject, user: GitUser, access_token: str, repo_path: Path
    ) -> None:
        self.token = access_token
        self.project = project

        self.user = user
        self.git = GitRepo(repo_path)
        self.remote_initialized = False

    def initialize_oath_remote(self):
        self.git.set_user(self.user)
        url_prefix = f"https://oauth2:{self.token}"
        url = f"{url_prefix}@{self.project.url}.git"
        remote = GitRemote("oath_origin", url)
        self.git.add_remote(remote)

    def push_change(self, message: str, target_branch="main", remote_name="origin"):

        if not self.remote_initialized:
            self.initialize_oath_remote()
            self.remote_initialized = True

        self.git.add_all()
        self.git.commit(message)
        self.git.push(remote_name, "HEAD", target_branch, "-o ci.skip")
