# adalab-cli

This repository contains the source code of `adalab-cli`, the CLI app to interact with the AdaLab platform.

## Installation

`adalab-cli` can be installed from PyPI or a `devpi` index:

```sh
# PyPI
pip install adalab-cli
# devpi
pip install --extra-index-url <devpi_index_url> adalab-cli
```

In order to add it to the dependencies of a Python project using `poetry` use:

```sh
poetry source add --priority=supplemental <repo_name> <devpi_index_url>
poetry source add --priority=primary PyPI
poetry add --source <repo_name> adalab-cli
```

## Usage

See the corresponding documentation pages.

## Contributing

See the [contributor's guide](CONTRIBUTING.md).
