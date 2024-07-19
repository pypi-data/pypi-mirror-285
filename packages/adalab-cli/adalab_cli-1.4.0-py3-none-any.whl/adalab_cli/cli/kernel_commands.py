"""Kernel-related commands for the adalib CLI.

This submodule provides commands for managing kernels in the adalib environment.
It includes functionalities such as installing new kernels, listing available kernels,
and other kernel management tasks.

Functions:
- install-kernel: Installs a new kernel.
"""

import typer
from adalib.lab import install_kernel

kernel_app = typer.Typer()


@kernel_app.command("install-kernel", no_args_is_help=True)
def kernel_install_kernel(
    image_name: str = typer.Argument(
        ...,
        help="Fully qualified OCI image name (e.g. `localhost/python:3.10`).",
    ),
    kernel_name: str = typer.Argument(
        ...,
        help="Name that the kernel should be displayed with in the Launcher.",
    ),
    language: str = typer.Option("python", help="Language of the kernel."),
    command: str = typer.Option("", help="Optional override command for the docker run."),
):
    """Installs a containerized kernel in the environment given an OCI image
    available in the users local container image registry.

    If called with only the two mandatory parameters, the kernel language will
    default to 'python' and the container run override command will be empty.

    Example usage:

    adalab kernels install-kernel localhost/py36:latest py36

    will install the locally available OCI image 'localhost/py36:latest' as a
    python kernel named 'py36'.
    """
    install_location = install_kernel(image_name, kernel_name, language, command)
    print(
        f"Installed kernel image {image_name}"
        f" as kernel {kernel_name}"
        f" at {install_location}"
    )
