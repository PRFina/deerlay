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
