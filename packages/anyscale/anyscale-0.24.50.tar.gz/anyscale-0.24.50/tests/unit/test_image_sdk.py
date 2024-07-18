from typing import Tuple

from common import TestLogger
import pytest

from anyscale import Anyscale
from anyscale._private.anyscale_client.fake_anyscale_client import FakeAnyscaleClient
from anyscale._private.models.image_uri import ImageURI
from anyscale._private.sdk.timer import FakeTimer
from anyscale.image import ImageSDK
from anyscale.image.models import ImageBuild, ImageBuildStatus


@pytest.fixture()
def image_sdk_with_fakes(
    sdk_with_fakes: Tuple[Anyscale, FakeAnyscaleClient, TestLogger, FakeTimer]
) -> Tuple[ImageSDK, FakeAnyscaleClient, TestLogger, FakeTimer]:
    sdk, client, logger, timer = sdk_with_fakes
    return sdk.image, client, logger, timer


class TestBuildImage:
    def test_build_image(
        self,
        image_sdk_with_fakes: Tuple[
            ImageSDK, FakeAnyscaleClient, TestLogger, FakeTimer
        ],
    ):
        sdk, fake_client, _, _ = image_sdk_with_fakes
        container_file = "\n".join(
            [
                "FROM docker.io/my/sofian-base-image:latest",
                'RUN pip install "requests"',
                'RUN pip install "flask"',
            ]
        )

        # call the SDK
        image_uri = sdk.build(container_file, name="bldname123", ray_version="2.24.0")

        assert image_uri, "Image URI is None"
        cluster_env_build_id = fake_client.get_cluster_env_build_id_from_image_uri(
            ImageURI.from_str(image_uri), ray_version="2.24.0"
        )
        assert fake_client._builds[cluster_env_build_id].containerfile == container_file


class TestGetImage:
    def test_get_image(
        self,
        image_sdk_with_fakes: Tuple[
            ImageSDK, FakeAnyscaleClient, TestLogger, FakeTimer
        ],
    ):
        sdk, fake_client, _, _ = image_sdk_with_fakes
        fake_client.get_cluster_env_build_id_from_containerfile(
            "my-image", "FROM python:3.8", anonymous=False, ray_version="2.24.0"
        )

        # call the sdk
        img_build = sdk.get(name="my-image")

        assert img_build == ImageBuild(
            status=ImageBuildStatus.SUCCEEDED,
            uri="anyscale/image/my-image:1",
            ray_version="2.24.0",
        )
