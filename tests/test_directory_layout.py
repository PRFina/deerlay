from pathlib import Path

import pytest

from deerlay import DirectoryLayout


class MockedkDirectoryLayout(DirectoryLayout):
    def discover(self):
        yield Path("file1.txt")
        yield Path("file2.txt")
        yield Path("file3.png")
        yield Path("file4.json")

    def parse(self, filepath):
        return filepath, {"field1": "value1", "field2": "value2"}


def test_directory_layout_init(tmp_path):
    collector = MockedkDirectoryLayout(tmp_path)
    assert collector.root_dir == tmp_path


def test_directory_layout_root_dir_not_exists():
    with pytest.raises(FileNotFoundError):
        MockedkDirectoryLayout("root/directory")


def test_directory_layout_collect(tmp_path):
    collector = MockedkDirectoryLayout(tmp_path)

    entries = list(collector.collect())

    assert entries[0][0] == collector.root_dir / "file1.txt"
    assert entries[1][0] == collector.root_dir / "file2.txt"
    assert entries[2][0] == collector.root_dir / "file3.png"
    assert entries[3][0] == collector.root_dir / "file4.json"

    expected_metadata = {"field1": "value1", "field2": "value2"}
    assert entries[0][1] == expected_metadata
    assert entries[1][1] == expected_metadata
    assert entries[2][1] == expected_metadata
    assert entries[3][1] == expected_metadata


def test_directory_layout_collect_with_path_selector(tmp_path):
    collector = MockedkDirectoryLayout(tmp_path)

    def json_selector(filepath):
        return bool(filepath.suffix == ".json")

    entries = list(collector.collect(path_selector=json_selector))

    assert len(entries) == 1
    assert entries[0][0] == collector.root_dir / "file4.json"
    assert entries[0][1] == {"field1": "value1", "field2": "value2"}


def test_directory_layout_collect_with_multiple_path_selector(tmp_path):
    collector = MockedkDirectoryLayout(tmp_path)

    def json_selector(filepath):
        return bool(filepath.suffix == ".json")

    def png_selector(filepath):
        return bool(filepath.suffix == ".png")

    selectors = [json_selector, png_selector]

    entries = list(collector.collect(path_selector=selectors, select_mode="any"))

    assert len(entries) == 2
    assert entries[0][0] == collector.root_dir / "file3.png"
    assert entries[1][0] == collector.root_dir / "file4.json"

    expected_metadata = {"field1": "value1", "field2": "value2"}
    assert entries[0][1] == expected_metadata
    assert entries[1][1] == expected_metadata


def test_directory_layout_collect_with_metadata_selector(tmp_path):
    collector = MockedkDirectoryLayout(tmp_path)

    def unknow_field(metadata):
        return "unknow_field" in metadata

    entries = list(collector.collect(metadata_selector=unknow_field))

    assert len(entries) == 0


def test_directory_layout_collect_with_augmenter(tmp_path):
    collector = MockedkDirectoryLayout(tmp_path)

    def field_adder(filepath, metadata):
        metadata["new_field"] = "new_value"

        return metadata

    entries = list(collector.collect(augmenter=field_adder))

    assert entries[0][0] == collector.root_dir / "file1.txt"
    assert entries[1][0] == collector.root_dir / "file2.txt"
    assert entries[2][0] == collector.root_dir / "file3.png"
    assert entries[3][0] == collector.root_dir / "file4.json"

    expected_metadata = {"field1": "value1", "field2": "value2", "new_field": "new_value"}
    assert entries[0][1] == expected_metadata
    assert entries[1][1] == expected_metadata
    assert entries[2][1] == expected_metadata
    assert entries[3][1] == expected_metadata


def test_directory_layout_collect_with_multiple_augmenter(tmp_path):
    collector = MockedkDirectoryLayout(tmp_path)

    def field_adder(filepath, metadata):
        metadata["new_field"] = "new_value"

        return metadata

    def field_remover(filepath, metadata):
        metadata.pop("new_field")

        return metadata

    augmenters = [field_adder, field_remover]
    entries = list(collector.collect(augmenter=augmenters))

    assert entries[0][0] == collector.root_dir / "file1.txt"
    assert entries[1][0] == collector.root_dir / "file2.txt"
    assert entries[2][0] == collector.root_dir / "file3.png"
    assert entries[3][0] == collector.root_dir / "file4.json"

    expected_metadata = {"field1": "value1", "field2": "value2"}
    assert entries[0][1] == expected_metadata
    assert entries[1][1] == expected_metadata
    assert entries[2][1] == expected_metadata
    assert entries[3][1] == expected_metadata
