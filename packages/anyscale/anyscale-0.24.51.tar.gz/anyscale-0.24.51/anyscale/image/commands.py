from typing import Optional

from anyscale._private.sdk import sdk_command
from anyscale.image._private.image_sdk import PrivateImageSDK
from anyscale.image.models import ImageBuild


_IMAGE_SDK_SINGLETON_KEY = "image_sdk"

_BUILD_EXAMPLE = """
import anyscale

containerfile = '''
FROM anyscale/ray:2.21.0-py39
RUN pip install --no-cache-dir pandas
'''

image_uri: str = anyscale.image.build(containerfile, name="mycoolimage")
"""

_BUILD_ARG_DOCSTRINGS = {
    "name": "The name of the image.",
    "containerfile": "The content of the Containerfile.",
    "ray_version": "The version of Ray to use in the image",
}


@sdk_command(
    _IMAGE_SDK_SINGLETON_KEY,
    PrivateImageSDK,
    doc_py_example=_BUILD_EXAMPLE,
    arg_docstrings=_BUILD_ARG_DOCSTRINGS,
)
def build(
    containerfile: str,
    *,
    name: str,
    ray_version: Optional[str] = None,
    _sdk: PrivateImageSDK
) -> str:
    """Build an image from a Containerfile.

    Returns the URI of the image.
    """
    return _sdk.build_image_from_containerfile_with_image_uri(
        name, containerfile, ray_version=ray_version
    )


_GET_EXAMPLE = """
import anyscale

image_status = anyscale.image.get(name="mycoolimage")
"""

_GET_ARG_DOCSTRINGS = {
    "name": (
        "Get the details of an image.\n\n"
        "The name can contain an optional version, e.g., 'name:version'. "
        "If no version is provided, the latest one will be used.\n\n"
    )
}


@sdk_command(
    _IMAGE_SDK_SINGLETON_KEY,
    PrivateImageSDK,
    doc_py_example=_GET_EXAMPLE,
    arg_docstrings=_GET_ARG_DOCSTRINGS,
)
def get(*, name: str, _sdk: PrivateImageSDK) -> ImageBuild:
    """The name can contain an optional version tag, i.e., 'name:version'.

    If no version is provided, the latest one will be returned.
    """
    return _sdk.get(name)
