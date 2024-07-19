from pathlib import Path
import shutil
from iccicd.repo import PythonRepo


def get_test_data_dir():
    return Path(__file__).parent / "data"


def test_increment_python_repo_version():

    repo_dir = get_test_data_dir() / "version_bump"
    shutil.copy(
        repo_dir / "testpyproject.toml", repo_dir / "testpyproject_working.toml"
    )
    shutil.copy(repo_dir / "docs" / "conf.xpy", repo_dir / "docs" / "conf_working.xpy")

    repo = PythonRepo(repo_dir)
    repo.pyproject.file_name = Path("testpyproject_working.toml")
    repo.sphinx.conf_path = Path("docs/conf_working.xpy")

    repo.increment_version("minor")

    pp_version = repo.pyproject.get_version()
    sphinx_version = repo.sphinx.get_version()
    (repo_dir / "testpyproject_working.toml").unlink()
    (repo_dir / "docs" / "conf_working.xpy").unlink()

    assert pp_version.major == 0
    assert pp_version.minor == 1
    assert pp_version.patch == 0

    assert sphinx_version.major == 0
    assert sphinx_version.minor == 1
    assert sphinx_version.patch == 0
