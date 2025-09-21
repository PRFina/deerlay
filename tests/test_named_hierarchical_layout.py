from pathlib import Path

import pytest

from deerlay import NamedHierarchicalLayout


@pytest.fixture
def named_hierarchical_directory_tree(tmp_path, dirtree_generator):
    root_dir = tmp_path
    dirtree_generator.build_dirtree_from_paths(
        tmp_path,
        paths=[
            "genre=planetary/year=1965/dune.txt",
            "genre=planetary/year=2011/the_martian.txt",
            "genre=planetary/year=2011/the_butcher_of_anderson_station.txt",
            "genre=dystopian/year=1949/1984.txt",
        ],
    )

    return root_dir


def test_named_hierarchical_layout_discover(named_hierarchical_directory_tree):
    collector = NamedHierarchicalLayout(named_hierarchical_directory_tree)
    entries = list(collector.discover())

    assert len(entries) == 4
    # order is important here
    assert entries[0] == named_hierarchical_directory_tree / "genre=dystopian/year=1949/1984.txt"
    assert entries[1] == named_hierarchical_directory_tree / "genre=planetary/year=1965/dune.txt"
    assert (
        entries[2]
        == named_hierarchical_directory_tree
        / "genre=planetary/year=2011/the_butcher_of_anderson_station.txt"
    )
    assert (
        entries[3]
        == named_hierarchical_directory_tree / "genre=planetary/year=2011/the_martian.txt"
    )


def test_named_hierarchical_layout_parse(tmp_path):
    collector = NamedHierarchicalLayout(tmp_path)

    filepath = tmp_path / "genre=planetary/year=2011/the_martian.txt"
    parsed_filepath, metadata = collector.parse(filepath)

    assert parsed_filepath == Path("genre=planetary/year=2011/the_martian.txt")
    assert metadata == {"genre": "planetary", "year": "2011", "filename": "the_martian.txt"}


def test_named_hierarchical_layout_parse_custom_field_name_delimiter(tmp_path):
    collector = NamedHierarchicalLayout(tmp_path, field_name_delimiter="$")

    filepath = tmp_path / "genre$planetary/year$2011/the_martian.txt"
    parsed_filepath, metadata = collector.parse(filepath)

    assert parsed_filepath == Path("genre$planetary/year$2011/the_martian.txt")
    assert metadata == {"genre": "planetary", "year": "2011", "filename": "the_martian.txt"}


def test_named_hierarchical_layout_collect(named_hierarchical_directory_tree):
    collector = NamedHierarchicalLayout(named_hierarchical_directory_tree)

    entries = list(collector.collect())

    assert entries[0][0] == collector.root_dir / "genre=dystopian/year=1949/1984.txt"
    assert entries[1][0] == collector.root_dir / "genre=planetary/year=1965/dune.txt"
    assert (
        entries[2][0]
        == collector.root_dir / "genre=planetary/year=2011/the_butcher_of_anderson_station.txt"
    )
    assert entries[3][0] == collector.root_dir / "genre=planetary/year=2011/the_martian.txt"

    assert entries[0][1] == {"genre": "dystopian", "year": "1949", "filename": "1984.txt"}
    assert entries[1][1] == {"genre": "planetary", "year": "1965", "filename": "dune.txt"}
    assert entries[2][1] == {
        "genre": "planetary",
        "year": "2011",
        "filename": "the_butcher_of_anderson_station.txt",
    }
    assert entries[3][1] == {"genre": "planetary", "year": "2011", "filename": "the_martian.txt"}
