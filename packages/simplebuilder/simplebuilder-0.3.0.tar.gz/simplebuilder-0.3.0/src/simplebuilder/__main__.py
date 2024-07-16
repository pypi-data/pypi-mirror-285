"""Make README more readable.

This file replaces relative path links with GitHub links and add warning in front of the long description.

Last modified at 2023-06-20; 12th edition.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import os
import re
import shutil
from pathlib import Path

import tomlkit

ProjectData = dict

cwd = Path.cwd()
pyproject_path = cwd / "pyproject.toml"

def build_parser():
    parser = argparse.ArgumentParser(
        "simplebuilder",
        "Simple build script for packages hosted on GitHub",
    )
    parser.add_argument("--no-readme", action="store_true", help="Delete readme after operation")
    # parser.add_argument("--no-install", action="store_true", help="Don't install current project.")
    parser.add_argument("--no-delete-dist", action="store_true", help="Don't delete `dist/` directory.")
    parser.add_argument("--upload", action="store_true", help="Upload project to PyPI. Requires PYPI_TOKEN environment variable.")
    parser.add_argument("--pub", "--publish-mode", "-P", action="store_true", help="shortcut of --no-readme --upload.")
    return parser


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    readme = not args.no_readme
    upload = args.upload
    delete_dist = args.no_delete_dist
    if args.pub:
        readme = False
        upload = True
    return readme, upload, delete_dist


def load_project_data() -> ProjectData:
    return tomlkit.parse(pyproject_path.read_text())


def match_url(url: str) -> tuple[str, str]:
    result = re.match(r"(https?:\/\/)?github[.]com\/(?P<user>\w+)\/(?P<project>\w+)", url)
    if result is None:
        raise ValueError("URL is invalid or not a github URL.")
    return result["user"], result["project"]


def replace_pyproject_version(version: str) -> None:
    pyproject_data = load_project_data()
    pyproject_data["tool"]["poetry"]["version"] = version  # type: ignore
    pyproject_path.write_text(tomlkit.dumps(pyproject_data), encoding="utf-8")


def build_readme(github_project_url: str, project_name: str, username: str) -> str:
    def make_relative_link_work(match: re.Match) -> str:
        if match.group("directory_type") in {"images", "image", "img"}:
            return (
                f'[{match.group("description")}](https://raw.githubusercontent.com/{username}'
                f'/{project_name}/master/{match.group("path")})'
            )

        return f'[{match.group("description")}]({github_project_url}/blob/master/{match.group("path")})'

    long_description = f"**Check latest version [here]({github_project_url}).**\n"
    long_description += Path("README.md").read_text(encoding="utf-8")
    long_description = re.sub(
        r"\[(?P<description>.*?)\]\(((\.\.\/)+|\.\/)(?P<path>(?P<directory_type>[^\/]*).*?)\)",
        make_relative_link_work,
        long_description,
    )
    return long_description


def upload_project():
    if "PYPI_TOKEN" not in os.environ:
        raise ValueError("Environment variable `PYPI_TOKEN` does not exist.")

    # Getting environment variable from `os.environ` makes this operation OS-independent.
    os.system(f'poetry publish -u __token__ -p {os.environ["PYPI_TOKEN"]}')


def main(argv=None):
    # parse args
    readme, upload, delete_dist = parse_args(argv=argv)

    # get data from pyproject
    project_data = load_project_data()
    build_data = project_data.get("tool", {}).get("simplebuild", {})
    name = (
        project_data.get("project", {}).get("name")
        or project_data.get("tool", {}).get("poetry", {}).get("name")
        # or cwd.name
    )
    project = importlib.import_module(name)
    url = build_data.get("github_url") or project.__url__
    version = project.__version__

    # construct github project url
    username, project_name = match_url(url)
    github_project_url = f"https://github.com/{username}/{project_name}"

    # remove dist if exist
    if delete_dist:
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree("dist")

    replace_pyproject_version(version)
    long_description = build_readme(github_project_url, name, username)

    readme_build = cwd / "README_build.md"
    try:
        readme_build.write_text(long_description, encoding="utf-8")

        os.system("poetry build")
        if upload:
            upload_project()
    finally:
        if not readme:
            with contextlib.suppress(FileNotFoundError):
                os.remove(readme_build)


if __name__ == "__main__":
    main()
