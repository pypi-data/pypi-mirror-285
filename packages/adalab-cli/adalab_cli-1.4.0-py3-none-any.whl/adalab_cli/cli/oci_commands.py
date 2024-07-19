"""OCI (Open Container Initiative) commands for the adalib CLI.

This submodule contains command functions for managing container images
and versions within the adalib CLI using Typer. It includes commands for
listing images, retrieving image versions, and other container-related operations.

Functions:
- get-images: Lists available container images for a specific image type.
- get-version: Retrieves version information for specific container images. (TODO)
"""

import sys

import typer
from adalib.adaboard import get_user
from adalib.harbor import get_container_images, get_image_versions
from tabulate import tabulate
from typing_extensions import Annotated

from .utils import get_environment_variable

oci_app = typer.Typer()


@oci_app.command("get-images", no_args_is_help=True)
def oci_get_container_images(
    image_type: Annotated[
        str,
        typer.Argument(
            help="The type of image to list. " "Choose from [kernels, apps, base_images].",
        ),
    ],
    pretty: Annotated[
        bool,
        typer.Option(help="Set this flag to get the output in a nice tabular view."),
    ] = False,
):
    """
    Prints the container images registered for IMAGE_TYPE.
    """
    user = get_user()
    try:
        container_images = get_container_images(
            project_name=image_type,
            username=user["username"],
            jh_token=get_environment_variable("JUPYTERHUB_API_TOKEN"),
        )
    except AssertionError as ae:
        sys.exit(f"Error: {str(ae)}")

    if pretty:
        print(f"{image_type} OCI images:")
        print(max([len(x) for x in container_images]) * "=")

    images_with_tags = []
    for image_name in container_images:
        image_name = image_name.replace(image_type + "/", "")
        images_with_tags.append(
            [
                image_name,
                get_image_versions(
                    project_name=image_type,
                    image_name=image_name,
                    username=user["username"],
                    jh_token=get_environment_variable("JUPYTERHUB_API_TOKEN"),
                ),
            ]
        )
    print(tabulate(images_with_tags, ["Image Name", "Image Tags (newest first)"]))


# @oci_app.command("push_image")
# def oci_push_container_image(name: str):
#    """
#    Pushes a container image identified by NAME to the adalab OCI registry
#    """
#    pass
