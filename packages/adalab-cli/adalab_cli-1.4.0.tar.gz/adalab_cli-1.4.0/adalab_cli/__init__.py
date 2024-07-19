"""The adalab-cli base module exposes the CLI application.
"""

import importlib.metadata

_DISTRIBUTION_METADATA = importlib.metadata.metadata("adalab-cli")
__project__ = _DISTRIBUTION_METADATA["name"]
__version__ = _DISTRIBUTION_METADATA["version"]
__description__ = _DISTRIBUTION_METADATA["description"]

__all__ = ["cli"]
