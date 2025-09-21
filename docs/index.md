# Deerlay

*Deerlay* is a lightweight, scope-limited, and dependency-free Python package crafted to streamline the discovery of files and the collection of associated metadata from datasets stored on disk, with different organizational structure.

This library stems from a simple yet compelling observation: while datasets may vary widely in structure—ranging from flat to deeply nested directories, with diverse naming conventions and partitioning schemes—the underlying *content* remains the same. The difference lies solely in the *form* or organization of the data.

Deerlay empowers users to focus on the data's content, providing a unified way to access and work with it.

??? Info "About Deerlay"
    Deerlay is a *malapropism* for "directory layout" 🧐. I'm not particularly clever, it's just that a `dirlay` package [already exists](https://github.com/makukha/dirlay). So, I had to get creative and came up with something that sounds similar.

    You `import deerlay`, but you say it like "dirlay".


## Quick Start
Suppose you want to fine-tune your pantagruelic LLM on science fiction topics. For semplicity, imagine you have a dataset organized into nested directories like this:

```plaintext
scifi_books/
    genre=planetary/
        year=1965/
            dune.pdf
            dune.txt
            dune.docx
        year=2011/
            the_martian.pdf
            the_martian.txt
            the_martian.docx
            the_butcher_of_anderson_station.pdf
            the_butcher_of_anderson_station.txt
            the_butcher_of_anderson_station.docx
    genre=dystopian/
        year=1949/
            1984.pdf
            1984.txt
            1984.docx
```

Before tokenizing and chunking the data, you need to access the files and read their content. Typically, you might use `dataset_dir.glob("**/*")` to collect file paths and then read the files with something like `with filepath.open("r") as fp`.

With `deerlay`, this process becomes a breeze. To get started, first [install](guide/install.md) the package.

Then:

```python
from deerlay import NamedHierarchicalLayout
from pathlib import Path

def text_selector(filepath: Path) -> bool:
    return filepath.suffix == ".txt"

collector = NamedHierarchicalLayout("scifi_books")

for filepath, metadata in collector.collect(path_selector=text_selector):
    print(filepath)
    print(metadata)
    print("------\n")
```

Running the above code produces the following output:

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

1. **File Discovery and Metadata Parsing**: As you iterate over `collector.collect`, `deerlay` discovers files and extracts metadata from their paths.
2. **File Filtering**: Only `.txt` files are selected, while others are filtered out based on the `text_selector` function.
3. **Metadata Transformation**: Metadata is parsed and presented in a structured format.

With `deerlay`, you can focus on processing your data without worrying about the complexities of file discovery and metadata extraction.

## Background and Related Projects

From a quick glance, it might seem that `deerlay` is just reinventing the wheel. However, there’s more to the story. After spending years developing Computer Vision (CV) Deep Learning models and maintaining several repositories, I noticed a recurring pattern: CV datasets often consist of numerous small multimedia files (e.g., images, videos) accompanied by additional data such as labels, masks, bounding boxes, and metadata. Over time, I realized that the same operations were being repeated: collecting file paths from disk, filtering out unwanted data, merging with supplementary information, and loading the file content into memory.

This pattern isn’t exclusive to CV datasets—it applies to other domains as well.

### Why Not Use Existing Tools?

Large Deep Learning frameworks like PyTorch and TensorFlow provide APIs for loading and processing data. However, these frameworks typically assume that the data is already formatted for ingestion (e.g., `.tfrecord` files) or leave the responsibility of crawling directories and collecting file paths to the user (e.g., `torch.utils.data.Dataset`). And that’s perfectly fine—these frameworks are primarily focused on making matrix multiplications efficient. 😏

Similarly, there are countless packages designed to efficiently load and process data once it’s in memory. Yet, the task of crawling directories and collecting files often feels like a third-class citizen in the ecosystem.

`deerlay` is built on the shoulders of giant. The API draws inspiration from several outstanding projects:

- **FiftyOne**: This project is incredible, and `deerlay` shares a similar spirit with its [Dataset Import API](https://docs.voxel51.com/user_guide/import_datasets.html). However, FiftyOne purpose if mainly for inspecting and debugging models. Moreover, is a large package with a complext API that cover a lot of uses case, with a steep learning curve. If you don’t need all the advanced features it offers, it might feel like overkill for simpler use cases.

- **Apache Arrow**: Another fantastic tool, but primarily designed for tabular data. Its Dataset API is vast and complex, and while it likely offers similar functionality to `deerlay`, those features are often buried under layers of legitimate complexity.

`deerlay` isn’t meant to replace these powerful tools. Instead, it aims to fill a gap by providing a lightweight, dependency-free solution for accessing datasets. It can complement these frameworks by simplifying the initial steps of file discovery and metadata extraction. For example, you could use `deerlay` to organize and preprocess your dataset before feeding it into a PyTorch `Dataset` or converting it into a format suitable for Apache Arrow.

By focusing on simplicity and usability, `deerlay` empowers users to spend less time wrangling files and more time working with their data.


## Releases and API Stability

`deerlay` adheres to semantic versioning, but it is currently in the `0.Y.Z` beta stage. This means the library is still under active development, and the public API is *not yet stable*. As we continue to refine and enhance the package, breaking changes are likely to occur in future updates before `1.0.0` stable release.

We encourage early adopters to explore `deerlay` and provide feedback, but please be mindful that the API may evolve as we work toward a more mature and stable release. Your input during this phase is invaluable in shaping the library's future direction ❤️‍🔥.
