from typing import Optional, Tuple

from common import TestLogger
import pytest

from anyscale import Anyscale
from anyscale._private.anyscale_client import FakeAnyscaleClient
from anyscale._private.sdk.timer import FakeTimer


@pytest.fixture()
def sdk_with_fakes() -> Tuple[Anyscale, FakeAnyscaleClient, TestLogger, FakeTimer]:
    timer = FakeTimer()
    logger = TestLogger()
    fake_client = FakeAnyscaleClient()
    return (
        Anyscale._init_private(client=fake_client, logger=logger, timer=timer),  # type: ignore
        fake_client,
        logger,
        timer,
    )
