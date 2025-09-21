## v0.1.0 (2025-09-22)

### BREAKING CHANGE

- `build_index_table` has been removed as it is premature
and requires a more thoughtful design. This minimizes the public API surface
and prevent pandas as dependency.
- the `collect` method now returns filepaths prefixed with
the root directory
- Renamed API methods, arguments, and class names to align with
a clearer and more consistent API design.

### Feat

- ensure consistent file discovery order
- add `file_extension_selector` utility to filter files by extension
- add callbacks for files filtering and metadata augmentation
- `collect` method returns relative filepaths without the root directory

### Fix

- wrong signature in discover abstract method

### Refactor

- remove build_index_table method
- enhance API naming for improved clarity and consistency
