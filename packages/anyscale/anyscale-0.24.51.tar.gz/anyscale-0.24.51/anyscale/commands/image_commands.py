from io import StringIO
from typing import IO, Optional

import click
import yaml

import anyscale


@click.group(
    "image", help="Manage images to define dependencies on Anyscale.",
)
def image_cli() -> None:
    pass


@image_cli.command(
    name="build", help=("Build an image from a Containerfile."),
)
@click.option(
    "--containerfile",
    "-f",
    help="Path to the Containerfile.",
    type=click.File("rb"),
    required=True,
)
@click.option(
    "--name",
    "-n",
    help="Name for the image. If the image with the same name already exists, a new version will be built. Otherwise, a new image will be created.",
    required=True,
    type=str,
)
@click.option(
    "--ray-version",
    "-r",
    help="The Ray version (X.Y.Z) specified for this image specified by either an image URI or a containerfile. If not provided, the latest Ray version will be used.",
    type=str,
    default=None,
)
def build(
    containerfile: IO[bytes], name: str, ray_version: Optional[str] = None
) -> None:
    containerfile_str = containerfile.read().decode("utf-8")
    image_uri = anyscale.image.build(
        containerfile_str, name=name, ray_version=ray_version
    )
    print(f"Image built successfully with URI: {image_uri}")


@image_cli.command(
    name="get", help=("Get details of an image."),
)
@click.option(
    "--name",
    "-n",
    help=(
        "Get the details of an image.\n\n"
        "The name can contain an optional version, e.g., 'name:version'. "
        "If no version is provided, the latest one will be used.\n\n"
    ),
    type=str,
    default=None,
    required=True,
)
def get(name: str) -> None:
    image_build = anyscale.image.get(name=name)
    stream = StringIO()
    yaml.safe_dump(image_build.to_dict(), stream, sort_keys=False)
    print(stream.getvalue(), end="")
