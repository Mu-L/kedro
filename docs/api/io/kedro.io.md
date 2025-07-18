# kedro.io

::: kedro.io
    options:
      docstring_style: google
      members: false
      show_source: false

| Name                                   | Type       | Description                                                                        |
|----------------------------------------|------------|------------------------------------------------------------------------------------|
| [`kedro.io.AbstractDataset`][] | Class      | Base class for all Kedro datasets.                                                 |
| [`kedro.io.AbstractVersionedDataset`][] | Class | Base class for versioned datasets.                                                 |
| [`kedro.io.CachedDataset`][]    | Class      | Dataset wrapper for caching data in memory.                                        |
| [`kedro.io.DataCatalog`][] | Class | Manages datasets used in a Kedro pipeline.                                         |
| [`kedro.io.CatalogProtocol`][] | Class | Defines a generic interface for managing datasets in a catalog.                    |
| [`kedro.io.SharedMemoryDataCatalog`][] | Class | Manages datasets used in a shared memory context.                                  |
| [`kedro.io.SharedMemoryCatalogProtocol`][] | Class | Extends `CatalogProtocol` to support shared memory use cases.                        |
| [`kedro.io.CatalogConfigResolver`][] | Class | Resolves dataset configurations based on dataset factory patterns and credentials. |
| [`kedro.io.MemoryDataset`][]    | Class      | Dataset for storing data in memory.                                                |
| [`kedro.io.Version`][]                | Class      | Represents dataset version information.                                            |
| [`kedro.io.DatasetAlreadyExistsError`][] | Exception | Raised when a dataset already exists.                                              |
| [`kedro.io.DatasetError`][]      | Exception  | General dataset-related error.                                                     |
| [`kedro.io.DatasetNotFoundError`][] | Exception | Raised when a dataset is not found.                                                |
