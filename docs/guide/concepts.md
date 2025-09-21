# Concepts

This guide introduce the main concepts around the `deerlay` API design with practical examples.


!!! Info
    For all the examples provided in this guide, we use a sample dataset called "*scifi books*". This dataset is available in the repository in the `tests/data/scifi_books` directory.

## Directory Layouts
A dataset, defined here as an *organized collection of files*, can exhibit a wide variety of structures. The way a dataset is structured often reflects the capabilities and constraints of the underlying storage system, such as an operating system file system or an object store (e.g., [MinIO](https://www.min.io/), [AWS's S3](https://aws.amazon.com/s3) or [GCP's Cloud Storage](https://cloud.google.com/storage) services).

Beside diffrences between storage technologies and the data content itself, dataset organization mainly arise from differences in *layouts*, how files are physical arranged within directories, and *naming*, the rules and conventions used to name files and directories.

The most natural types of organization for datasets include *flat* or *hierarchical* layouts.


=== "Flat Layout"
    Files are organized directly under a single root directory without any nested directories. This layout resembles a [star tree](https://en.wikipedia.org/wiki/Star_(graph_theory)) with a single root node (the root directory) and only leaf nodes (files) directly beneath it.

    ```tree
    root
        file1.ext
        file2.ext
        file3.ext
        ...
        fileN.ext
    ```
    It's simplicity makes file location straightforward, as there are no intermediate levels to navigate.



=== "Hierarchical Layout (or Nested)"
    Files can be organized either at the top-level or within nested subdirectories, resembling the structure of a [N-ary tree](https://en.wikipedia.org/wiki/M-ary_tree). In this analogy, the root directory serves as the root node, while the nested directories act as internal nodes, and the files themselves are the leaf nodes.

    ```tree
    root
        dir1/
            file1.ext
            file2.ext
            subdir1/
                file3.ext
                file4.ext
        dir2/
            subdir/
                subsubdir/
                    .../
                        file5.ext
        ...
        fileN.ext
    ```

    This hierarchical structure allows for better categorization and organization of releated data, making it easier to navigate and manage large datasets.

=== "Partition Layout"
    The *Partition Layout* is a highly structured variation of the Hierarchical layout. In this layout, all files are stored **only** at the last level of the directory tree.

    ```tree
    root
        dir1/
            subdir1/
                ...
                    file1.ext
                    file2.ext
        ../
        dirN/
            subdirN/
                ...
                    file1.ext
                    file2.ext
    ```
    This strict organization is particularly useful when consistent file location is required, as it simplifies the process of querying and filtering data.

!!! Note
    This guide focuses exclusively on local storage and  file systems, as `deerlay` does not (yet) support remote object storages.

## Naming Conventions
Beyond the structural relationships among files and directories defined by a layout, *naming* play a pivotal role in conveying meaning and further organization within datasets.

By embedding metadata directly into filepaths, files become more discoverable. This approach provides immediate context about a file's contents-such as its category, creation date, or other relevant attributes - without requiring external metadata sources. This practice is especially valuable fore large datasets where efficient querying and filtering are essential.

For example, consider the *scifi books* sample dataset. By encoding *metadata fields* like genre and publication year into the filepaths (e.g., `planetary$1965$dune.pdf`), you can instantly locate all books within a specific genre or from a particular year. This reduces the need to open, parse and inspect individual file contents, which is a significantly more time-consuming task (both for human and machines).

=== "Flat"
    ```tree
    scifi_books:
        planetary$1965$dune.pdf
        planetary$2011$the_martian.pdf
        planetary$2011$the_butcher_of_anderson_station.pdf
        dystopian$1949$1984.pdf
    ```

=== "Partition"
    ```tree
        scifi_books:
            planetary
                1965
                    dune.pdf
                2011
                    the_martian.pdf
                    the_butcher_of_anderson_station.pdf
            dystopian
                1949
                    1984.pdf
    ```

However, the statement above is not entirely accurate. With a naming convention like `planetary$1965$dune.pdf`, the *field names* (e.g., "genre" or "year") are **implicit** and the meaning of the fields remain ambiguous.

This ambiguity can lead to confusion or misinterpretation. For example, consider a filepath like `aXi394343ds/9384XGs8u3h/dune.pdf`. While a human might guess that these *high-entropy* fields represent some kind of unique identifiers (e.g., an ISBN code or an internal organizational ID), the exact meaning remains unclear ^^without additional context^^. Machines, which can't speculate (yet 🙄), have a much harder time reliably parsing or interpreting this metadata.

To address this issue, a common approach is to **explicitly** encode field names within the filepath. This reduces ambiguity by directly associating each field value with its corresponding name, making the dataset more *self-descriptive*, improving machine-readability and reducing the need for external information.

For instance, the *scifi books* dataset above could be represented with explicit field names as follows:

=== "Flat"
    ```tree
    scifi_books:
        genre=planetary$year=1965$dune.pdf
        genre=planetary$year=2011$the_martian.pdf
        genre=planetary$year=2011$the_butcher_of_anderson_station.pdf
        genre=dystopian$year=1949$1984.pdf
    ```

=== "Partition"
    ```tree
    scifi_books:
        genre=planetary
            year=1965
                dune.pdf
            year=2011
                the_martian.pdf
                the_butcher_of_anderson_station.pdf
        genre=dystopian
            year=1949
                1984.pdf
    ```
    This format is also known as, [Hive Partitioning](https://duckdb.org/docs/stable/data/partitioning/hive_partitioning.html#hive-partitioning).

## Datasets in `deerlay`

`deerlay` is built on a simple yet effective *logical model* for file paths, which allows it to abstract away different file organizations:

=== "Flat"

    ![](../assets/filepath_structure_flat.svg){ align=center }


=== "Hierarchical"
    ![](../assets/filepath_structure_hierarchical.svg){ align=center }

- *Root Directory*: The dataset top-level directory and the base path for all files within it.
- *Fields*: Metadata attributes encoded in the segments of a file path.
- *Field Delimiter*: A character, (e.g. `$`) , that separates metadata fields. In a hierarchical layout, this is implicitly the operating system's directory separator  (e.g., `/` on Unix-like systems, `\` on Windows).
- *Field Name Delimiter*: A character (e.g., `=`) that separates an ^^optional^^ *field name* from its *value*.
- *Filename*: the last segment of a file path.

The various `*DirectoryLayout` classes in `deerlay` establish a common API for accessing files and their encoded metadata. For example, consider these layouts:

=== "Flat"
    ```tree
    scifi_books:
        planetary$1965$dune.pdf
        planetary$2011$the_martian.pdf
        planetary$2011$the_butcher_of_anderson_station.pdf
        dystopian$1949$1984.pdf
    ```
    You can use the `FlatLayout` class:

    ```py
    from deerlay import FlatLayout

    collector = FlatLayout(
        root_dir="scifi_books",
        fields=["genre","year"],
        field_delimiter="$"
    )

    ```

=== "Flat (with field names)"
    ```tree
    scifi_books:
        genre=planetary$year=1965$dune.pdf
        genre=planetary$year=2011$the_martian.pdf
        genre=planetary$year=2011$the_butcher_of_anderson_station.pdf
        genre=dystopian$year=1949$1984.pdf
    ```
    You can use the `NamedFlatLayout` class:
    ```py
    from deerlay import NamedFlatLayout

    collector = NamedFlatLayout(
        root_dir="scifi_books",
        field_name_delimiter="=",
        field_delimiter="$"
    )

    ```
=== "Hierarchical"
    ```tree
        scifi_books:
            planetary
                1965
                    dune.pdf
                2011
                    the_martian.pdf
                    the_butcher_of_anderson_station.pdf
            dystopian
                1949
                    1984.pdf
    ```
    You can use the `HierarchicalLayout`:
    ```py
    from deerlay import HierarchicalLayout

    collector = HierarchicalLayout(
        root_dir="scifi_books",
        fields=["genre","year"]
    )
    ```
=== "Hierarchical (with field names)"
    ```tree
    scifi_books:
        genre=planetary
            year=1965
                dune.pdf
            year=2011
                the_martian.pdf
                the_butcher_of_anderson_station.pdf
        genre=dystopian
            year=1949
                1984.pdf

    ```
    You can use:
    ```py
    from deerlay import NamedHierarchicalLayout

    collector = NamedHierarchicalLayout(
        root_dir="scifi_books",
        field_name_delimiter="="
    )

    ```

!!! Warning "Delimiter Collision"
    Delimiters, such as `$` or `=`, must be chosen carefully to prevent [collisions](https://en.wikipedia.org/wiki/Delimiter#Delimiter_collision) with characters that might naturally appear in field names and values.

    For this reason, the `deerlay` API expose the `field_name_delimiter` and `field_delimiter` arguments, to let user choose which delimiter is more suitable to prevent collisions.

## The Collection Loop

After discussing file organization, we will now cover the process of discovering and collecting files.

The *Collection Loop* is the core iterative process in `deerlay`. It crawls a dataset's directories to find files and parse metadata from their paths. Its high-level logic is best understood through the following pseudocode:

```py title="The Collection Loop"
def collect(root_dir): # (1)!
    for filepath in discover(root_dir): #(2)!
        metadata = parse(filepath) #(3)!
        return filepath, metadata
```

1. Although this uses Python syntax, consider it pseudocode.
2. The `discover` function crawls the directory tree starting from `root_dir` to [yield](https://docs.python.org/3/reference/expressions.html#yield-expressions) file paths.
3. The `parse` function parses metadata fields from a file path and yields a metadata dictionary in the format of `{field_name: field_value}`.

Each Directory Layout class provided in `deerlay` API:

- Inherits from the `DirectoryLayout` base class. This class has the built-in implementation of the Collection Loop within the `collect` method.
- Implements the `discover` and `parse` abstract methods based on the specific organization of data.

??? Example
    Let's consider the *scifi books* dataset:
    ```tree
    scifi_books:
        genre=planetary
            year=1965
                dune.txt
            year=2011
                the_martian.txt
                the_butcher_of_anderson_station.txt
        genre=dystopian
            year=1949
                1984.txt
    ```

    To collect data:

    ```py hl_lines="5"
    from deerlay import NamedHierarchicalLayout

    collector = NamedHierarchicalLayout("scifi_books", delimiter="=")

    for filepath, metadata in collector.collect():
        print(filepath)
        print(metadata)
        print("------\n")

    ```
    Calling the `collect()` method returns a [generator](https://docs.python.org/3/glossary.html#term-generator-iterator) that, when iterated, yields a filepath and parsed metadata for each discovered file.

    Running the above snippet, the output will be:
    ```
    scifi_books/genre=dystopian/year=1949/1984.txt
    {'genre': 'dystopian', 'year': '1949', 'filename': '1984.txt'}
    ------

    scifi_books/genre=planetary/year=1965/dune.txt
    {'genre': 'planetary', 'year': '1965', 'filename': 'dune.txt'}
    ------

    scifi_books/genre=planetary/year=2011/the_butcher_of_anderson_station.txt
    {'genre': 'planetary', 'year': '2011', 'filename': 'the_butcher_of_anderson_station.txt'}
    ------

    scifi_books/genre=planetary/year=2011/the_martian.txt
    {'genre': 'planetary', 'year': '2011', 'filename': 'the_martian.txt'}
    ------
    ```


!!! Note "Listing Order"
    The order on which files and directories are listed is arbitrary and implementation depedendent, i.e. could varies accross different operating systems, filesystems, and Python distributions.

    Currently, `deerlay` directory layouts enforce an **alphanumerical ascending ordering** by default, to assure reproducibility. See [issue#3](https://github.com/PRFina/deerlay/issues/3) for more information.


## Collecting and Filtering FIles
A dataset often contains multiple related files, but not all of them may be necessary. To address this, some files can be filtered and discarded, while others are selected and retained.

To handle these use cases, `deerlay` provides a simple mechanism called *Selectors*. Selectors are just functions (or callables) with a specific signature:

=== "Path Selector"
    A *Path Selector* is a function that takes the ==file path== of a discovered file and contains the logic to select or filter it. If the function returns True, the file is selected and further processed. If it returns False, the file is "blocked" and discarded.

    ```py
    def path_selector(filepath:Path) -> bool
        ...
    ```

=== "Metadata Selector"
    A *Metadata Selector* is a function that takes the ==metadata dictionary== of a discovered file and contains the logic to select or filter it. If the function returns True, the file is selected and further processed. If it returns False, the file is blocked and discarded.

    ```py
    def meta_selector(metadata:dict[str,str]) -> bool
        ...
    ```


Selectors are injected into the Collection Loop at specific points:

```py hl_lines="3 5"
def collect(root_dir, path_selector, metadata_selector):
    for filepath in discover(roo_dir):
        if path_selector(filepath)
            metadata = parse(filepath)
            if metadata_selector(metadata)
                return filepath, metadata
```

The two different selector types are provided primarily for *efficiency*:

- If your selection logic can be determined by inspecting only the file path, use a Path Selector. This approach is more efficient because it skips the more computationally intensive task of parsing a file's metadata.

- If your selection logic is based on the file's metadata, use a Metadata Selector.

??? Example
    Consider *scifi books* dataset, with some additional file formats:
    ```tree
    scifi_books:
        genre=planetary
            year=1965
                dune.pdf
                dune.txt
                dune.docx
            year=2011
                the_martian.pdf
                the_martian.txt
                the_martian.docx
                the_butcher_of_anderson_station.pdf
                the_butcher_of_anderson_station.txt
                the_butcher_of_anderson_station.docx
        genre=dystopian
            year=1949
                1984.pdf
                1984.txt
                1984.docx
    ```
    Let consider that you're only interested in working with one format, let's say the `.txt`. This is a perfect use case for a Path Selector:

    ```py hl_lines="3 4 9"
    from deerlay import NamedHierarchicalLayout

    def text_selector(filepath:Path) -> bool:
        return filepath.suffix == ".txt"

    collector = NamedHierarchicalLayout("scifi_books")

    for filepath, metadata in collector.collect(
        path_selector=text_selector
    ):
        print(filepath)
        print(metadata)
        print("------\n")
    ```
    While iterating the `collector.collect` iterator, only the books in `.txt` will be selected while others will be filtered out:

    ```
    scifi_books/genre=dystopian/year=1949/1984.txt
    {'genre': 'dystopian', 'year': '1949', 'filename': '1984.txt'}
    ------

    scifi_books/genre=planetary/year=1965/dune.txt
    {'genre': 'planetary', 'year': '1965', 'filename': 'dune.txt'}
    ------

    scifi_books/genre=planetary/year=2011/the_butcher_of_anderson_station.txt
    {'genre': 'planetary', 'year': '2011', 'filename': 'the_butcher_of_anderson_station.txt'}
    ------

    scifi_books/genre=planetary/year=2011/the_martian.txt
    {'genre': 'planetary', 'year': '2011', 'filename': 'the_martian.txt'}
    ------
    ```

    !!! Tip
        For convenience, `deerlay.callbacks` module offers pre-built utility selectors like `file_extension_selector` that are ready for use in common scenarios.

    ---

    Now let's consider that for some reason, you need to work only with books older than 2000. Since this information is encoded in the `year` field, you can define a Metadata selector:

    ```py hl_lines="6 7 8 14"
    from deerlay import NamedHierarchicalLayout

    def text_selector(filepath:Path) -> bool:
        return filepath.suffix == ".txt"

    def only_old_books(metadata:dict[str,str]) -> bool:
        publication_year = int(metadata["year"]) #(1)!
        return publication_year < 2000

    collector = NamedHierarchicalLayout("scifi_books")

    for filepath, metadata in collector.collect(
        path_selector=text_selector,
        metadata_selector=only_old_books
    ):
        print(filepath)
        print(metadata)
        print("------\n")
    ```

    1. Notice that you need to cast the field value to a proper type since field names and values are always parsed as `str`.

    In this case the only books yielded will be `1984.txt` and `dune.txt` as they both match the selection conditions:

    ```
    scifi_books/genre=dystopian/year=1949/1984.txt
    {'genre': 'dystopian', 'year': '1949', 'filename': '1984.txt'}
    ------

    scifi_books/genre=planetary/year=1965/dune.txt
    {'genre': 'planetary', 'year': '1965', 'filename': 'dune.txt'}
    ------
    ```


Selectors can also be a convenient way for *adapting* datasets whose layout isn't fully supported by `deerlay`.

For example, consider the a slightly different *scifi books* dataset like this:
```tree
scifi_books:
    genre=planetary
        year=1965
            dune.txt
        year=2011
            the_martian.txt
            the_butcher_of_anderson_station.txt
        planetary_metadata.csv
    genre=dystopian
        year=1949
            1984.txt
        dystopian_metadata.csv
```

As you can see, the presence of `planetary_metadata.csv` and `dystopian_metadata.csv` files doesn't conform to the [Partition Layout](#__tabbed_1_3). This is because they are not stored at the deepest level of the directory tree and do not follow the required naming convention.

In this case, you can use a selector to discard these files.

```py hl_lines="3 4 9"
from deerlay import NamedHierarchicalLayout

def discard_genre_metadata_files(filepath:Path) -> bool:
    return not (filepath.suffix == ".csv" and "_metadata" in filepath.stem)

collector = NamedHierarchicalLayout("scifi_books")

for filepath, metadata in collector.collect(
    metadata_selector=discard_genre_metadata_files
):
    print(filepath)
    print(metadata)
    print("------\n")
```
Outputs:
```
scifi_books/genre=dystopian/year=1949/1984.txt
{'genre': 'dystopian', 'year': '1949', 'filename': '1984.txt'}
------

scifi_books/genre=planetary/year=1965/dune.txt
{'genre': 'planetary', 'year': '1965', 'filename': 'dune.txt'}
------

scifi_books/genre=planetary/year=2011/the_butcher_of_anderson_station.txt
{'genre': 'planetary', 'year': '2011', 'filename': 'the_butcher_of_anderson_station.txt'}
------

scifi_books/genre=planetary/year=2011/the_martian.txt
{'genre': 'planetary', 'year': '2011', 'filename': 'the_martian.txt'}
------
```

!!! Tip
    If this is a frequent use case, we encourage you to check out the guide on [implementing custom layouts](extending.md) or contribute to the project by [opening a new issue](https://github.com/PRFina/deerlay/issues/new)!.


### Complex Filtering

While you can express all your filtering logic in a single, complex function, it's often better to compose it from multiple smaller, `reusable` functions. deerlay facilitates this by allowing the `path_selector` and `metadata_selector` arguments to accept either a single function or a collection (list or tuple) of selector functions.

When a list of selectors is provided, `deerlay` processes each one in sequence, applying them to the file path or metadata dict in a pipeline-like fashion. However, when using multiple selectors, it is crucial to understand the `selection_mode` argument and how it affects the final results. There are two supported selection modes:

- `all`: With this mode, a file is selected only if **all** selectors in the list return True. If even one selector returns False, the file is discarded. This behavior is similar to a [logical conjunction]((https://en.wikipedia.org/wiki/Logical_conjunction) ) (the `and` operator). This is the default mode.

    ??? Example
        ```py hl_lines="11 15"
        from deerlay import NamedHierarchicalLayout

        def text_selector(filepath:Path) -> bool:
            return filepath.suffix == ".txt"

        def pdf_selector(filepath:Path) -> bool:
            return filepath.suffix == ".pdf"

        collector = NamedHierarchicalLayout("scifi_books")

        selectors = [text_selector, pdf_selector]

        for filepath, metadata in collector.collect(
            path_selector=selectors,
            selection_mode="all"
        ):
            ...
        ```
        The code above will return an empty iterator because no file can have both a `.txt` **and** a `.pdf` extension simultaneously.

- `any`: With this mode, a file is selected if **any** selector in the list returns True. A file is only discarded if all selectors return False. This behavior is similar to a [logical disjunction](https://en.wikipedia.org/wiki/Logical_disjunction) (the `or` operator).

    ??? Example
        ```py hl_lines="11 15"
        from deerlay import NamedHierarchicalLayout

        def text_selector(filepath:Path) -> bool:
            return filepath.suffix == ".txt"

        def pdf_selector(filepath:Path) -> bool:
            return filepath.suffix == ".pdf"

        collector = NamedHierarchicalLayout("scifi_books")

        selectors = [text_selector, pdf_selector]

        for filepath, metadata in collector.collect(
            path_selector=selectors,
            selection_mode="any"
        ):
            ...
        ```

        The code above will returnreturn all books with a `.txt` *or* a `.pdf` extension.

Keep the following key considerations in mind:

- The `selection_mode` is **global**. The same `selection_mode` applies to both the `path_selector` and `metadata_selector` arguments. Currently, you can't specify a different mode for each argument.

- When you pass a list of multiple selectors to either the `path_selector` or `metadata_selector` argument, `deerlay` applies every function in that list to each discovered file/parsed metadata. The boolean values returned by these functions are then evaluated together using the specified `selection_mode`. This process is applied **independently** for each selector type.

- Metadata selectors are only applied to files that have not been filtered out by the path selectors.




!!! Note "Reusable Selectors"
    You can define selectors that accept arguments. This allows you to create reusable, *parameterized* functions.

    For example, a selector that filters books older than a specific year could be defined as follows:

    ```py
    def books_older_than(metadata:dict[str,str], year:int) -> bool:
        publication_year = int(metadata["year"])
        return publication_year < year
    ```

    To use this function as a selector, you can use `functools.partial` to pre-set or "bind" the argument value:

    ```py hl_lines="3 9"
    from functools import partial

    books_older_than_2000 = partial(books_older_than, year=2000)

    collector = NamedHierarchicalLayout("scifi_books")

    for filepath, metadata in collector.collect(
        path_selector=text_selector,
        metadata_selector=books_older_than_2000
    ):
        ...
    ```


## Collecting and Augmenting Metadata
While a file's path can encode some metadata, it often doesn't contain all the information you need. Conversely, the default parsing process might extract metadata you don't require or that needs to be modified.

To handle these cases, `deerlay` provides a simple mechanism called *Augmenters*.

While Augmenters and Selectors are programmatically similar, they serve a *distinct purpose*: Selectors are designed to filter out unwanted. Augmenters are used to modify the parsed metadata of files that have already been selected.

Aside from this key difference in purpose, they are implemented in a very similar way:


- An augmenter is a function (or callable) with a specific signature. It takes the file path and the parsed metadata dictionary as input, and returns a modified metadata dictionary:
    ```py
    def augmenter(filepath:Path, metadata:dict[str,str]) -> dict[str,str]
        ... # logic to add, remove, or change metadata fields
    ```

- Augmenters can be used wrapped in a list, in which case they are applied sequentially to the metadata of each file.
    ```py hl_lines="7"
    def augmenter_1(filepath:Path, metadata:dict[str,str]) -> dict[str,str]
        ...

    def augmenter_2(filepath:Path, metadata:dict[str,str]) -> dict[str,str]
        ...

    augmenters = [augmenter_1, augmenter_2]

    collector.collect(..., augmenter=augmenters)
    ```


- As with selectors, augmenters are injected into the *Collection Loop* at a specific point, acting as the final step before a file is returned.

    ```py hl_lines="6"
    def collect(root_dir, path_selector, metadata_selector, augmenter):
        for filepath in discover(roo_dir):
            if path_selector(filepath)
                metadata = parse(filepath)
                if metadata_selector(metadata)
                    metadata = augmenter(filepath, metadata)
                    return filepath, metadata
    ```

??? Example
    Consider the *scifi books* dataset:
    ```tree
    scifi_books:
        genre=planetary
            year=1965
                dune.pdf
            year=2011
                the_martian.pdf
                the_butcher_of_anderson_station.pdf
        genre=dystopian
            year=1949
                1984.pdf
    ```
    Let's suppose that you want to enrich the parsed metadata with some metadata about stored files (like size, creation date, etc.).

    ```py

    def file_size_augmenter(filepath:Path, metadata:dict[str,str]):
        stats = Path(filepath).stat()

        metadata["file_size"] = f"{stats.st_size}B"

        return metadata

    def filename_formatter(filepath:Path, metadata:dict[str,str]):
        filename = metadata.pop("filename")
        metadata["title"] = filename.split(".")[0].replace("_","-")

        return metadata
    ```

    Now you can pass the augmenters to the `collect` method:

    ```py
    from deerlay import NamedHierarchicalLayout

    collector = NamedHierarchicalLayout("scifi_books", delimiter="=")
    augmenters = [file_size_augmenter, filename_formatter]

    for filepath, metadata in  collector.collect():
        print(filepath)
        print(metadata)
        print("------\n")

    ```
    It return a [generator](https://docs.python.org/3/glossary.html#term-generator-iterator) that when iterated yield a filepath and **augmented** metadata as a dict. In the case of the snippet above will output something like:
    ```
    scifi_books/genre=dystopian/year=1949/1984.txt
    {'genre': 'dystopian', 'year': '1949', 'file_size': '2407B', 'title': '1984'}
    ------

    scifi_books/genre=planetary/year=1965/dune.txt
    {'genre': 'planetary', 'year': '1965', 'file_size': '10032B', 'title': 'dune'}
    ------

    scifi_books/genre=planetary/year=2011/the_butcher_of_anderson_station.txt
    {'genre': 'planetary', 'year': '2011', 'file_size': '1003B', 'title': 'the-butcher-of-anderson-station'}
    ------

    scifi_books/genre=planetary/year=2011/the_martian.txt
    {'genre': 'planetary', 'year': '2011', 'file_size': '5017B', 'title': 'the-martian'}
    ------
    ```


!!! Warning

    When you use pass a list of augmenters, it's crucial to understand how they interact.

    Augmenters process a single metadata dictionary instance that is passed from one to the next. This means any changes made by an augmenter, such as adding, modifying, or deleting a field, will be visible to all subsequent augmenters in the list.

    Because of this **shared state**, it's important that each augmenter *merge* its new data with the original dictionary and return the combined result. This ensures data from previous augmenters is not lost.

    === "👉 Right"
        ```py
        from datetime import datetime

        def augmenter(filepath:Path, metadata:dict[str,str]):
            stats = Path(filepath).stat()

            file_stats = {
                "file_size"  f"{stats.st_size}B"
                "last_access": datetime.fromtimestamp(stats.st_atime).strftime("%Y-%m-%d %H:%M:%S")
            }

            return metadata | file_stats
        ```
    === "👎 Wrong"

        ```py
        from datetime import datetime

        def augmenter(filepath:Path, metadata:dict[str,str]):
            stats = Path(filepath).stat()

            file_stats = {
                "file_size"  f"{stats.st_size}B"
                "last_access": datetime.fromtimestamp(stats.st_atime).strftime("%Y-%m-%d %H:%M:%S")
            }

            return file_stats
        ```


## Takeaways & Next Steps

You've covered a lot of ground 🌟 To help you on your way, here's a quick summary of the key takeaways:

- **File Organization** 🗂️: While file organization varies widely, it generally falls into two categories: flat or hierarchical layouts.
- **Naming and Metadata** 🏷️: Embedding metadata directly into file paths via a naming convention improves data discoverability and access efficiency.
- **Explicit vs. Implicit Names** 👀: Explicitly naming fields makes the dataset more self-descriptive improving the its machine-readability. This practice eliminates the need to pass field names via the `field_names` argument while instantiating `*DirectoryLayout` objects.
- **The Collection Loop** 🔄: Is the core process implemented in the `collect` method. It discovers dataset files and parses metadata fields from their paths. Its default behavior is highly customizable using *Selector* and *Augmenter* callback functions.
- **Selectors** 🧹: You can filter unwanted data by using one or more Selectors with the `path_selector` and `metadata_selector` arguments of the `collect` method 🤏.
- **Augmenters** ✨: You can modify parsed metadata - adding new fields, removing existing ones, or changing values, by using one or more Augmenters with the `augmenter` argument of the `collect` method.

Ready for the next step? You can continue your journey with deerlay by:

- Exploring further customization. Check out the [extending deerlay](extending.md) guide to learn how to implement your own directory layouts.
