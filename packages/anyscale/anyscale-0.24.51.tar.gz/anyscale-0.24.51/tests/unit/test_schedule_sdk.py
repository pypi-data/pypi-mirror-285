from typing import Tuple

from common import OPENAPI_NO_VALIDATION, TestLogger
import pytest

from anyscale import Anyscale
from anyscale._private.anyscale_client import FakeAnyscaleClient
from anyscale._private.sdk.timer import FakeTimer
from anyscale.client.openapi_client.models.decorated_schedule import DecoratedSchedule
from anyscale.client.openapi_client.models.production_job_config import (
    ProductionJobConfig,
)
from anyscale.client.openapi_client.models.schedule_config import (
    ScheduleConfig as BackendScheduleConfig,
)
from anyscale.job.models import JobConfig
from anyscale.schedule import ScheduleSDK
from anyscale.schedule.models import ScheduleConfig, ScheduleState, ScheduleStatus


@pytest.fixture()
def schedule_sdk_with_fakes(
    sdk_with_fakes: Tuple[Anyscale, FakeAnyscaleClient, TestLogger, FakeTimer]
) -> Tuple[ScheduleSDK, FakeAnyscaleClient, TestLogger, FakeTimer]:
    sdk, client, logger, timer = sdk_with_fakes
    return sdk.schedule, client, logger, timer


class TestApply:
    def test_basic(
        self,
        schedule_sdk_with_fakes: Tuple[
            ScheduleSDK, FakeAnyscaleClient, TestLogger, FakeTimer
        ],
    ):
        sdk, fake_client, _, _ = schedule_sdk_with_fakes

        job_config = JobConfig(entrypoint="python hello.py", name="test-job-name",)
        config = ScheduleConfig(
            job_config=job_config, cron_expression="0 0 * * * *", timezone="UTC",
        )

        schedule_id = sdk.apply(config)
        created_schedule = fake_client.get_schedule(
            id=schedule_id, name=None, cloud=None, project=None
        )

        expected_schedule = DecoratedSchedule(
            id=schedule_id,
            name=job_config.name,
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint=job_config.entrypoint,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                max_retries=1,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            schedule=BackendScheduleConfig(
                cron_expression=config.cron_expression, timezone=config.timezone
            ),
            next_trigger_at=fake_client.SCHEDULE_NEXT_TRIGGER_AT_TIME,
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )

        assert created_schedule is not None
        assert created_schedule == expected_schedule


class TestSetState:
    def test_basic(
        self,
        schedule_sdk_with_fakes: Tuple[
            ScheduleSDK, FakeAnyscaleClient, TestLogger, FakeTimer
        ],
    ):
        sdk, fake_client, _, _ = schedule_sdk_with_fakes

        name = "test-job-name"
        job_config = JobConfig(entrypoint="python hello.py", name=name)
        config = ScheduleConfig(
            job_config=job_config, cron_expression="0 0 * * * *", timezone="UTC",
        )

        schedule_id = sdk.apply(config)
        assert fake_client.schedule_is_enabled(schedule_id)

        sdk.set_state(id=schedule_id, state=ScheduleState.DISABLED)
        assert not fake_client.schedule_is_enabled(schedule_id)

        sdk.set_state(id=schedule_id, state=ScheduleState.ENABLED)
        assert fake_client.schedule_is_enabled(schedule_id)

        sdk.set_state(name=name, state=ScheduleState.DISABLED)
        assert not fake_client.schedule_is_enabled(schedule_id)

        sdk.set_state(name=name, state=ScheduleState.ENABLED)
        assert fake_client.schedule_is_enabled(schedule_id)


class TestStatus:
    def test_schedule_not_found(
        self,
        schedule_sdk_with_fakes: Tuple[
            ScheduleSDK, FakeAnyscaleClient, TestLogger, FakeTimer
        ],
    ):
        sdk, fake_client, _, _ = schedule_sdk_with_fakes

        with pytest.raises(
            RuntimeError, match="Schedule with name 'test-schedule-name' was not found."
        ):
            sdk.status(name="test-schedule-name")

    def test_basic(
        self,
        schedule_sdk_with_fakes: Tuple[
            ScheduleSDK, FakeAnyscaleClient, TestLogger, FakeTimer
        ],
    ):
        sdk, fake_client, _, _ = schedule_sdk_with_fakes

        name = "test-job-name"
        job_config = JobConfig(
            entrypoint="python hello.py",
            name=name,
            compute_config=f"{fake_client.DEFAULT_CLUSTER_COMPUTE_NAME}:1",
        )
        config = ScheduleConfig(
            job_config=job_config, cron_expression="0 0 * * * *", timezone="UTC",
        )

        schedule_id = sdk.apply(config)

        expected_schedule_status = ScheduleStatus(
            config=config, name=name, id=schedule_id, state=ScheduleState.ENABLED
        )
        assert sdk.status(id=schedule_id) == expected_schedule_status

        sdk.set_state(id=schedule_id, state=ScheduleState.DISABLED)

        expected_schedule_status = ScheduleStatus(
            config=config, name=name, id=schedule_id, state=ScheduleState.DISABLED
        )
        assert sdk.status(id=schedule_id) == expected_schedule_status


class TestTrigger:
    def test_basic(
        self,
        schedule_sdk_with_fakes: Tuple[
            ScheduleSDK, FakeAnyscaleClient, TestLogger, FakeTimer
        ],
    ):
        sdk, fake_client, _, _ = schedule_sdk_with_fakes

        name = "test-job-name"
        job_config = JobConfig(
            entrypoint="python hello.py",
            name=name,
            compute_config=f"{fake_client.DEFAULT_CLUSTER_COMPUTE_NAME}:1",
        )
        config = ScheduleConfig(
            job_config=job_config, cron_expression="0 0 * * * *", timezone="UTC",
        )

        schedule_id = sdk.apply(config)
        assert fake_client.trigger_counts(schedule_id) == 0

        sdk.trigger(id=schedule_id)
        assert fake_client.trigger_counts(schedule_id) == 1

        sdk.trigger(name=name)
        assert fake_client.trigger_counts(schedule_id) == 2
