from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path

PathSelector = Callable[[Path], bool]
MetaSelector = Callable[[dict[str, str]], bool]
Augmenter = Callable[[Path, dict[str, str]], dict[str, str]]


def noop_path_selector(path: Path):
    return True


def noop_metadata_selector(meta: dict[str, str]):
    return True


def noop_augmenter(path, meta):
    return meta


def apply_selectors(
    item: Path | dict[str, str],
    selectors: MetaSelector | PathSelector | Iterable[MetaSelector] | Iterable[PathSelector],
    reducer=all,
) -> bool:
    if not isinstance(selectors, Iterable):
        selectors = [selectors]

    return reducer(func(item) for func in selectors)


def apply_augmenters(filepath, metadata, augmenters: Augmenter | list[Augmenter]):
    if not isinstance(augmenters, Iterable):
        augmenters = [augmenters]

    for augmenter in augmenters:
        metadata = augmenter(filepath, metadata)
    return metadata


def add_file_stats(filepath, metadata, time_format="%Y-%m-%dT%H:%M:%S"):
    stats = Path(filepath).stat()

    metadata["file_size"] = stats.st_size
    metadata["file_last_access"] = datetime.fromtimestamp(stats.st_atime).strftime(time_format)
    metadata["file_last_modification"] = datetime.fromtimestamp(stats.st_mtime).strftime(
        time_format
    )
    metadata["file_last_change"] = datetime.fromtimestamp(stats.st_ctime).strftime(time_format)

    return metadata


def file_extension_selector(filepath: Path, extensions: Iterable[str]) -> bool:
    """
    Check if the file extension of the given filepath matches any of the specified extensions.

    Notes:
        - File extensions must be prefixed with a ".", e.g., use ".txt" instead of "txt".
        - Matching is performed on the entire extension as whole,
        not its subparts (use {".tar.gz"} instead of {".tar", ".gz"}).
        - Matching is case-sensitive. To ensure robustness, include both
        lowercase and uppercase variations (e.g., {".png", ".PNG"}).


    Args:
        filepath (Path): The path of the file to check.
        extensions (Iterable[str]): A collection of file extensions to match against.

    Returns:
        bool: True if the file's extension matches **any** of the specified extensions,
        False otherwise.
    """
    return "".join(filepath.suffixes) in extensions
