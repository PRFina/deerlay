import os
from pathlib import Path

import pytest


class DirTreeGenerator:
    """
    DirTreeGenerator is a utility class for creating directory trees on disk based on
    nested dictionary structures  or lists of str paths with optional file content.
    """

    @staticmethod
    def build_dirtree(rootdir: str | Path, dirtree: dict[str, dict | str | None]):
        """
        Build a directory tree on disk that mirrors the structure of a nested dictionary.

        """
        rootdir = Path(rootdir)
        rootdir.mkdir(exist_ok=True)
        for key, value in dirtree.items():
            current_path = rootdir / key

            if isinstance(value, dict):
                # Recursively create subdirectories
                current_path.mkdir(parents=True, exist_ok=True)
                DirTreeGenerator.build_dirtree(current_path, value)
            elif isinstance(value, str) or not value:
                # Create a file in the current directory
                current_path.touch()
                if value:
                    with current_path.open("w") as f:
                        f.write(value)

    @staticmethod
    def build_dirtree_from_paths(rootdir: str | Path, paths: list[str], value=None):
        """
        Build a directory tree on disk from a list of paths.

        Args:
            rootdir (str|Path): The root directory where the tree will be created.
            dotlist (list[str]): List of dot-separated paths representing files and directories.

        Example:
            pathlist = [
                "folder1/subfolder1/file1.txt",
                "folder1/subfolder1/file2.txt",
                "folder1/subfolder2/file3.txt",
                "folder2/file4.txt"
            ]
            DirTreeGenerator.build_dirtree_from_paths(Path("output_directory"), pathlist)
        """

        dirtree = DirTreeGenerator._pathlist_to_dict(paths, value=value)
        DirTreeGenerator.build_dirtree(rootdir, dirtree)

    @staticmethod
    def _pathlist_to_dict(pathlist: list[str], value=None) -> dict:
        """_summary_

        Args:
            pathlist (list[str]): _description_
            value (_type_, optional): _description_. Defaults to None.

        Returns:
            dict: _description_
        """
        merged_dict = {}
        for path in pathlist:
            keys = path.split(os.sep)
            current = merged_dict
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = value
        return merged_dict


@pytest.fixture
def dirtree_generator():
    return DirTreeGenerator
