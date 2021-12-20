import os
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path

from tomlkit import parse
from tomlkit.toml_document import TOMLDocument


@contextmanager
def change_directory(path: Path) -> None:
    origin = Path().absolute()

    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def get_extras(pyproject: TOMLDocument) -> list[str]:
    tool = pyproject.get('tool', {})
    poetry = tool.get('poetry', {})
    extras = poetry.get('extras', {})
    return list(extras.keys())


def update_env(pyproject_path: Path) -> None:
    project_path = env.parent

    venv = project_path / '.venv'

    with pyproject_path.open() as pyproject_file:
        pyproject = parse(pyproject_file.read())
        extras = get_extras(pyproject)

    env = os.environ.copy()
    del env["VIRTUAL_ENV"]

    with change_directory(project_path):
        shutil.rmtree(venv, ignore_errors=True)

        subprocess.run(['poetryup'], env=env)

        subprocess.run(['poetry', 'update'], env=env)

        extras_args = [arg for extra in extras for arg in ['-E', extra]] if extras else []
        subprocess.run(['poetry', 'install', *extras_args], env=env)


def update_envs(workspace: Path) -> None:
    pyproject_tomls = workspace.glob('**/pyproject.toml')

    for pyproject_path in pyproject_tomls:
        update_env(pyproject_path)


if __name__ == '__main__':
    update_envs(Path('..'))
