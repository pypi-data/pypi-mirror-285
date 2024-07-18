from dataclasses import dataclass
import os
import re
from typing import Optional

import pytest
import tzlocal

from anyscale.job.models import JobConfig
from anyscale.schedule.models import ScheduleConfig, ScheduleState, ScheduleStatus


@dataclass
class ScheduleConfigFile:
    name: str
    expected_config: Optional[ScheduleConfig] = None
    expected_error: Optional[str] = None

    def get_path(self) -> str:
        return os.path.join(
            os.path.dirname(__file__), "test_files/schedule_config_files", self.name
        )


TEST_CONFIG_FILES = [
    ScheduleConfigFile(
        "empty.yaml",
        expected_error=re.escape(
            "__init__() missing 2 required positional arguments: 'job_config' and 'cron_expression'"
        ),
    ),
    ScheduleConfigFile(
        "minimal.yaml",
        expected_config=ScheduleConfig(
            cron_expression="0 0 * * * *",
            job_config=JobConfig(entrypoint="python test.py"),
        ),
    ),
    ScheduleConfigFile(
        "full.yaml",
        expected_config=ScheduleConfig(
            cron_expression="0 0 * * * *",
            timezone="local",
            job_config=JobConfig(
                name="test-name-from-file",
                image_uri="docker.io/library/test:latest",
                compute_config="test-compute-config",
                working_dir="test-working-dir",
                excludes=["test"],
                requirements=["pip-install-test"],
                entrypoint="python test.py",
                max_retries=5,
            ),
        ),
    ),
    ScheduleConfigFile(
        "unrecognized_option.yaml",
        expected_error=re.escape(
            "__init__() got an unexpected keyword argument 'bad_option'"
        ),
    ),
]


class TestScheduleConfig:
    def test_invalid_config(self):
        with pytest.raises(TypeError, match="'job_config' must be a JobConfig"):
            ScheduleConfig(job_config=None, cron_expression="0 0 * * * *")

        with pytest.raises(TypeError, match="'job_config' must be a JobConfig"):
            ScheduleConfig(job_config="job_config", cron_expression="0 0 * * * *")

    def test_invalid_cron_expression(self):
        job_config = JobConfig(entrypoint="python main.py")

        with pytest.raises(TypeError, match="'cron_expression' must be a string"):
            ScheduleConfig(job_config=job_config, cron_expression=None)

        with pytest.raises(ValueError, match="'cron_expression' cannot be empty"):
            ScheduleConfig(job_config=job_config, cron_expression="")

    def test_invalid_timezone(self):
        job_config = JobConfig(entrypoint="python main.py")
        cron_exp = "0 0 * * * *"
        with pytest.raises(TypeError, match="'timezone' must be a string"):
            ScheduleConfig(
                job_config=job_config, cron_expression=cron_exp, timezone=123,
            )

        with pytest.raises(ValueError, match="'timezone' cannot be empty"):
            ScheduleConfig(job_config=job_config, cron_expression=cron_exp, timezone="")

    def test_basic(self):
        job_config = JobConfig(entrypoint="python main.py")
        cron_exp = "0 0 * * * *"

        conf = ScheduleConfig(job_config=job_config, cron_expression=cron_exp)
        assert conf.timezone == "UTC"
        assert conf.cron_expression == cron_exp

        conf = ScheduleConfig(
            job_config=job_config, cron_expression=cron_exp, timezone="local"
        )
        assert conf.timezone == tzlocal.get_localzone_name()
        assert conf.cron_expression == cron_exp

        tz_name = "America/Los_Angeles"
        conf = ScheduleConfig(
            job_config=job_config, cron_expression=cron_exp, timezone=tz_name
        )
        assert conf.timezone == tz_name
        assert conf.cron_expression == cron_exp

    @pytest.mark.parametrize("config_file", TEST_CONFIG_FILES)
    def test_from_yaml(self, config_file):
        if config_file.expected_error is not None:
            with pytest.raises(Exception, match=config_file.expected_error):
                ScheduleConfig.from_yaml(config_file.get_path())

            return

        assert config_file.expected_config == ScheduleConfig.from_yaml(
            config_file.get_path()
        )


class TestScheduleStatus:
    @pytest.mark.parametrize(
        "state", [ScheduleState.ENABLED, ScheduleState.DISABLED,],
    )  # type: ignore
    def test_version_states(self, state: ScheduleState):
        # id, name, state, config
        assert (
            ScheduleStatus(
                id="test-schedule-id",
                name="test-schedule-name",
                state=state,
                config=ScheduleConfig(
                    cron_expression="0 0 * * * *",
                    job_config=JobConfig(entrypoint="python test.py"),
                ),
            ).state
            == state
        )

    def test_unknown_states(self):
        with pytest.raises(
            ValueError, match="'NOT_REAL_STATE' is not a valid ScheduleState"
        ):
            ScheduleStatus(
                id="test-schedule-id",
                name="test-schedule-name",
                state="NOT_REAL_STATE",
                config=ScheduleConfig(
                    cron_expression="0 0 * * * *",
                    job_config=JobConfig(entrypoint="python test.py"),
                ),
            )
