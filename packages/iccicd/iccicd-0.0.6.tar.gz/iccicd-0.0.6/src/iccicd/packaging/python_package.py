from pathlib import Path
import logging

from iccore import process


logger = logging.getLogger(__name__)


class PyPiContext:
    def __init__(self, token: str, use_test_repo: bool) -> None:
        self.token = token
        self.use_test_repo = use_test_repo


class PythonPackage:
    def __init__(self, repo_path: Path) -> None:
        self.repo_path = repo_path

    def build(self):
        logger.info("Building Python package")
        output_dir = self.repo_path / "dist"
        cmd = f"python3 -m build --outdir {output_dir} {self.repo_path}"
        process.run(cmd)
        logger.info("Finished building Python package")

    def upload(self, pypi_context: PyPiContext):
        logger.info("Uploading Python package")

        if not pypi_context.token:
            raise RuntimeError("Provided PyPi token cannot be empty")

        repo = ""
        if pypi_context.use_test_repo:
            repo = " -r testpypi "

        token = f"-p {pypi_context.token}"
        upload_dir = self.repo_path / "dist"
        cmd = f"twine upload {upload_dir}/*  --non-interactive {token} {repo}"
        process.run(cmd)
        logger.info("Finished uploading Python package")
