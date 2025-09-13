from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable
import os
from pathlib import Path
import re
from typing import Literal

import pandas as pd

from .callbacks import (
    Augmenter,
    MetaSelector,
    PathSelector,
    apply_augmenters,
    apply_selectors,
    noop_augmenter,
    noop_metadata_selector,
    noop_path_selector,
)

FileEntry = tuple[Path, dict[str, str]]
FileEntries = Iterable[FileEntry]


NOT_ALLOWED_DELIMITERS = {
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


def check_delimiter(field_name_delimiter: str) -> bool:
    if field_name_delimiter in NOT_ALLOWED_DELIMITERS:
        msg = f"'{field_name_delimiter}' character is not allowed as field_name_delimiter. \
                Select another one not included in {NOT_ALLOWED_DELIMITERS}"
        raise ValueError(msg)


class DirectoryLayout(ABC):
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        if not self.root_dir.exists():
            raise FileNotFoundError(f"Root directory '{self.root_dir}' does not exist.")

    def collect(
        self,
        path_selector: PathSelector | Iterable[PathSelector] = None,
        metadata_selector: MetaSelector | Iterable[MetaSelector] = None,
        augmenter: Augmenter | Iterable[Augmenter] = None,
        select_mode: Literal["all", "any"] = "all",
    ) -> Generator[FileEntry, None, None]:
        if select_mode not in ("all", "any"):
            raise ValueError("select_mode must be either 'all' or 'any'")
        reducer = all if select_mode == "all" else any

        # if given use them, otherwise use no-op function
        path_selector = path_selector or noop_path_selector
        metadata_selector = metadata_selector or noop_metadata_selector
        augmenter = augmenter or noop_augmenter

        # collection loop
        for filepath in self.discover():
            if apply_selectors(filepath, path_selector, reducer):
                filepath, metadata = self.parse(filepath)
                if apply_selectors(metadata, metadata_selector, reducer):
                    full_filepath = self.get_fullpath(filepath)
                    metadata = apply_augmenters(full_filepath, metadata, augmenter)

                    yield full_filepath, metadata

    @abstractmethod
    def discover(self) -> Generator[Path, None, None]:
        pass

    @abstractmethod
    def parse(self, filepath: Path) -> FileEntry:
        pass

    def get_fullpath(self, filename, as_absolute=False) -> Path:
        filepath = self.root_dir / filename
        return filepath.absolute() if as_absolute else filepath

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
    def __init__(self, root_dir: Path, fields: list[str], field_delimiter: str = "$"):
        super().__init__(root_dir)
        check_delimiter(field_delimiter)

        self.fields = fields
        self.field_delimiter = field_delimiter
        self._discover_pattern = "*.*"
        self._pattern = re.compile(rf"([^{field_delimiter}]+)")

    def discover(self) -> Generator[Path, None, None]:
        yield from self.root_dir.glob(self._discover_pattern)

    def parse(self, filepath: Path) -> FileEntry:
        filepath = filepath.relative_to(self.root_dir)

        matches = re.findall(self._pattern, str(filepath))
        meta = dict(zip(self.fields, matches, strict=False))

        return filepath, meta


class NamedFlatLayout(DirectoryLayout):
    def __init__(self, root_dir: Path, field_name_delimiter: str = "=", field_delimiter: str = "$"):
        super().__init__(root_dir)
        check_delimiter(field_name_delimiter)
        check_delimiter(field_delimiter)

        self.field_delimiter = field_delimiter
        self._discover_pattern = "*.*"
        self._pattern = re.compile(
            rf"([^${field_name_delimiter}]+){field_name_delimiter}([^${field_delimiter}\.]+)"
        )

    def discover(self) -> Generator[Path, None, None]:
        yield from self.root_dir.glob(self._discover_pattern)

    def parse(self, filepath: Path) -> FileEntry:
        filepath = filepath.relative_to(self.root_dir)

        matches = re.findall(self._pattern, filepath.name)
        meta = dict(matches)

        return filepath, meta


class HierarchicalLayout(DirectoryLayout):
    """_summary_

    Args:
        DirectoryLayout (_type_): _description_
    """

    def __init__(self, root_dir: Path, fields: list[str]) -> None:
        super().__init__(root_dir)
        self.field_delimiter = os.path.sep
        self.fields = fields
        self._pattern = re.compile(rf"([^{self.field_delimiter}]+)")

    def discover(self) -> Generator[Path, None, None]:
        for dirpath, _, filenames in os.walk(self.root_dir):
            if filenames:
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    yield filepath

    def parse(self, filepath: Path) -> FileEntry:
        filepath = filepath.relative_to(self.root_dir)
        dirpath, filename = filepath.parent, filepath.name

        meta = dict(zip(self.fields, dirpath.parts, strict=False))
        meta["filename"] = filename

        return filepath, meta


class NamedHierarchicalLayout(DirectoryLayout):
    def __init__(self, root_dir: Path, field_name_delimiter: str = "="):
        super().__init__(root_dir)
        check_delimiter(field_name_delimiter)
        self.keyval_separator = field_name_delimiter

    def discover(self) -> Generator[Path, None, None]:
        for dirpath, _, filenames in os.walk(self.root_dir):
            if filenames:
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    yield filepath

    def parse(self, filepath: Path) -> FileEntry:
        filepath = filepath.relative_to(self.root_dir)
        dirpath, filename = filepath.parent, filepath.name

        meta = dict(part.split(self.keyval_separator, 1) for part in dirpath.parts)
        meta["filename"] = filename

        return filepath, meta
