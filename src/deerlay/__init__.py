from collections.abc import Callable, Generator, Iterable
import os
from pathlib import Path
import re
from typing import Any

import pandas as pd

FileEntry = tuple[Path, dict[str, str]]
FileEntries = Iterable[FileEntry]


NOT_ALLOWED_SEPARATORS = {
    "/",
    "\\",
    ":",
    "*",
    "?",
    "<",
    ">",
    '"',
    "|",
}


# TODO declare as ABC
class DirectoryLayout:
    def __init__(self, root_dir: Path, keyval_separator="="):
        if keyval_separator in NOT_ALLOWED_SEPARATORS:
            msg = f"'{keyval_separator}' character is not allowed as separator. \
                Select another one not included in {NOT_ALLOWED_SEPARATORS}"
            raise ValueError(msg)

        self.root_dir = Path(root_dir)
        if not self.root_dir.exists():
            raise FileNotFoundError(f"Root directory '{self.root_dir}' does not exist.")

        self.keyval_separator = keyval_separator

    def discover(self) -> Generator[FileEntries, None, None]:
        raise NotImplementedError

    def get_fullpath(self, filename, as_absolute=False) -> Path:
        filepath = self.root_dir / filename
        return filepath.absolute() if as_absolute else filepath

    def _parse_entry(self, filepath: Path) -> FileEntry:
        raise NotImplementedError

    def build_index_table(
        self,
        entries: FileEntries,
        index_fields: str | list[str] | None = None,
        add_filepath: bool = False,
    ):
        if add_filepath:
            record_generator = (
                entry[1] | {"filepath": str(self.get_fullpath(entry[0]))} for entry in entries
            )
        else:
            record_generator = (entry[1] for entry in entries)

        index = pd.DataFrame.from_records(record_generator, index=index_fields)

        return index


class FlatLayout(DirectoryLayout):
    def __init__(self, root_dir: Path, fields: list[str], field_separator: str = "$"):
        super().__init__(root_dir, None)
        self.fields = fields
        self.field_separator = field_separator
        self._discover_pattern = "*.*"
        self._pattern = re.compile(rf"([^{field_separator}]+)")

    def discover(self):
        for path in Path(self.root_dir).glob(self._discover_pattern):
            yield self._parse_entry(path)

    def _parse_entry(self, filepath: Path):
        filepath = filepath.relative_to(self.root_dir)

        matches = re.findall(self._pattern, str(filepath))
        parsed_components = dict(zip(self.fields, matches, strict=False))

        return filepath, parsed_components


class HierarchicalLayout(DirectoryLayout):
    """_summary_

    Args:
        DirectoryLayout (_type_): _description_
    """

    def __init__(
        self, root_dir: Path, fields: list[str], segment_separator: str = os.path.sep
    ) -> None:
        super().__init__(root_dir, None)
        self.segment_separator = segment_separator
        self.fields = fields
        self._pattern = re.compile(rf"([^{segment_separator}]+)")

    def discover(self, filter_func: Callable[[FileEntry], bool] | None = None) -> Any:
        for dirpath, _, filenames in os.walk(self.root_dir):
            if filenames:
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    yield self._parse_entry(filepath)

    def _parse_entry(self, filepath: Path) -> tuple[Path, dict[str, str]]:
        filepath = filepath.relative_to(self.root_dir)

        matches = re.findall(self._pattern, str(filepath))
        parsed_components = dict(zip(self.fields, matches, strict=False))

        return filepath, parsed_components


class FlatLayoutWithKey(DirectoryLayout):
    def __init__(self, root_dir: Path, keyval_separator: str = "=", field_separator: str = "$"):
        super().__init__(root_dir, keyval_separator)
        self.field_separator = field_separator
        self._discover_pattern = "*.*"
        self._pattern = re.compile(
            rf"([^${keyval_separator}]+){keyval_separator}([^${field_separator}\.]+)"
        )

    def discover(self):
        for path in Path(self.root_dir).glob(self._discover_pattern):
            yield self._parse_entry(path)

    def _parse_entry(self, filepath: Path):
        filepath = filepath.relative_to(self.root_dir)
        matches = re.findall(self._pattern, filepath.name)

        # Convert matches into a dictionary
        parsed_components = dict(matches)
        return filepath, parsed_components


class HierarchicalLayoutWithKey(DirectoryLayout):
    def __init__(self, root_dir: Path, keyval_separator: str = "=", segment_separator: str = "$"):
        super().__init__(root_dir, keyval_separator)
        self.segment_separator = segment_separator
        self._pattern = re.compile(
            rf"([^${keyval_separator}]+){keyval_separator}([^${segment_separator}\.]+)"
        )

    def discover(self) -> Any:
        for dirpath, _, filenames in os.walk(self.root_dir):
            if filenames:
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    yield self._parse_entry(filepath)

    def _parse_entry(self, filepath: Path) -> tuple[Path, dict[str, str]]:
        filepath = filepath.relative_to(self.root_dir)
        for part in filepath.parts:
            matches = re.findall(self._pattern, part)
            parsed_components = dict(matches)

        return filepath, parsed_components
