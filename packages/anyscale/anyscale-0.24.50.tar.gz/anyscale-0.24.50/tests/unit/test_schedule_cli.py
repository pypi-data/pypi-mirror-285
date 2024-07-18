from collections import defaultdict
import os
from typing import Dict, Generator, Optional
import uuid

import click
from click.testing import CliRunner
import pytest

from anyscale._private.sdk import _LAZY_SDK_SINGLETONS
from anyscale.commands.schedule_commands import apply, pause, resume, status, trigger
from anyscale.job.models import JobConfig
from anyscale.schedule.commands import _SCHEDULE_SDK_SINGLETON_KEY
from anyscale.schedule.models import ScheduleConfig, ScheduleState, ScheduleStatus


def _get_test_file_path(subpath: str) -> str:
    return os.path.join(os.path.dirname(__file__), "test_files/", subpath)


EMPTY_CONFIG_PATH = _get_test_file_path("schedule_config_files/empty.yaml")
MINIMAL_CONFIG_PATH = _get_test_file_path("schedule_config_files/minimal.yaml")
FULL_CONFIG_PATH = _get_test_file_path("schedule_config_files/full.yaml")
UNRECOGNIZED_OPTION_CONFIG_PATH = _get_test_file_path(
    "schedule_config_files/unrecognized_option.yaml"
)

FULL_CONFIG_SCHEDULE_NAME = "test-name-from-file"


class FakeScheduleSDK:
    DEFAULT_SCHEDULE_NAME = "default-fake-schedule-name"

    def __init__(self):
        self.applied_config: Optional[ScheduleConfig] = None
        self.applied_id: Optional[str] = None
        self.applied_name: Optional[str] = None
        self._schedule_is_paused: Dict[str, bool] = {}
        self._schedule_trigger_counts: Dict[str, int] = defaultdict(int)

    def apply(self, config: ScheduleConfig):
        assert isinstance(config, ScheduleConfig)
        self.applied_config = config
        self.applied_id = str(uuid.uuid4())

        job_config = self.applied_config.job_config
        assert isinstance(job_config, JobConfig)
        self.applied_name = (
            job_config.name
            if job_config.name is not None
            else self.DEFAULT_SCHEDULE_NAME
        )
        self._schedule_is_paused[self.applied_id] = False
        self._schedule_is_paused[self.applied_name] = False
        return self.applied_id

    def set_state(
        self,
        *,
        id: Optional[str] = None,  # noqa: A002
        name: Optional[str] = None,
        cloud: Optional[str] = None,
        project: Optional[str] = None,
        state: ScheduleState,
    ) -> str:
        is_paused = state == ScheduleState.DISABLED
        if name is not None:
            self._schedule_is_paused[name] = is_paused
        elif id is not None:
            self._schedule_is_paused[id] = is_paused

        return id if id is not None else ""

    def schedule_is_paused(self, identifier: str) -> bool:
        return self._schedule_is_paused[identifier]

    def status(
        self,
        *,
        id: Optional[str] = None,  # noqa: A002
        name: Optional[str] = None,
        cloud: Optional[str] = None,
        project: Optional[str] = None,
    ) -> ScheduleStatus:
        if (
            self.applied_config is not None
            and self.applied_name is not None
            and (name == self.applied_name or id == self.applied_id)
        ):
            if name is not None:
                is_paused = self._schedule_is_paused[name]
            elif id is not None:
                is_paused = self._schedule_is_paused[id]

            state = ScheduleState.DISABLED if is_paused else ScheduleState.ENABLED
            return ScheduleStatus(
                id=self.applied_id if self.applied_id else "",
                name=self.applied_name,
                state=state,
                config=self.applied_config,
            )
        raise RuntimeError("Schedule was not found.")

    def trigger(
        self,
        *,
        id: Optional[str] = None,  # noqa: A002
        name: Optional[str] = None,
        cloud: Optional[str] = None,
        project: Optional[str] = None,
    ) -> str:
        if name is not None:
            self._schedule_trigger_counts[name] += 1
        elif id is not None:
            self._schedule_trigger_counts[id] += 1

        return id if id is not None else ""

    def trigger_counts(self, identifier: str) -> int:
        return self._schedule_trigger_counts[identifier]


@pytest.fixture()
def fake_schedule_sdk() -> Generator[FakeScheduleSDK, None, None]:
    fake_schedule_sdk = FakeScheduleSDK()
    _LAZY_SDK_SINGLETONS[_SCHEDULE_SDK_SINGLETON_KEY] = fake_schedule_sdk
    try:
        yield fake_schedule_sdk
    finally:
        del _LAZY_SDK_SINGLETONS[_SCHEDULE_SDK_SINGLETON_KEY]


def _assert_error_message(result: click.testing.Result, *, message: str):
    assert result.exit_code != 0
    assert message in result.stdout


class TestApply:
    def test_missing_arg(self, fake_schedule_sdk):
        runner = CliRunner()
        result = runner.invoke(apply)
        _assert_error_message(
            result, message="Error: Missing option '--config-file' / '-f'."
        )

    def test_config_file_not_found(self, fake_schedule_sdk):
        runner = CliRunner()
        result = runner.invoke(apply, ["-f", "missing_config.yaml"])
        _assert_error_message(
            result, message="Schedule config file 'missing_config.yaml' not found.",
        )

    @pytest.mark.parametrize(
        "config_file_arg", [MINIMAL_CONFIG_PATH, FULL_CONFIG_PATH],
    )
    def test_basic(self, fake_schedule_sdk, config_file_arg):
        runner = CliRunner()
        result = runner.invoke(apply, ["-f", config_file_arg])
        assert result.exit_code == 0, result.stdout
        assert fake_schedule_sdk.applied_config is not None

    def test_override_name(self, fake_schedule_sdk):
        runner = CliRunner()
        name = "test-different-name"
        result = runner.invoke(apply, ["--name", name, "-f", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert result.exit_code == 0, result.stdout
        assert fake_schedule_sdk.applied_config is not None
        assert fake_schedule_sdk.applied_name == name


class TestPauseResume:
    @pytest.mark.parametrize("command", [pause, resume])
    def test_no_identifiers(self, command, fake_schedule_sdk):
        runner = CliRunner()
        result = runner.invoke(command)
        _assert_error_message(
            result,
            message="One of '--name', '--id', or '--config-file' must be provided.",
        )

    @pytest.mark.parametrize("command", [pause, resume])
    @pytest.mark.parametrize(
        "identifiers",
        [
            ("name", "config_file", None),
            ("name", None, "id"),
            (None, "config_file", "id"),
            ("name", "config_file", "id"),
        ],
    )
    def test_multi_identifiers(self, command, identifiers, fake_schedule_sdk):
        runner = CliRunner()
        args = []
        name, config_file, id = identifiers  # noqa: A001
        if name:
            args += ["--name", name]
        if config_file:
            args += ["--config-file", config_file]
        if id:
            args += ["--id", id]

        result = runner.invoke(command, args)
        _assert_error_message(
            result,
            message="Only one of '--name', '--id', and '--config-file' can be provided.",
        )

    def test_name(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        assert not fake_schedule_sdk.schedule_is_paused(FULL_CONFIG_SCHEDULE_NAME)

        result = runner.invoke(pause, ["--name", FULL_CONFIG_SCHEDULE_NAME])
        assert result.exit_code == 0
        assert fake_schedule_sdk.schedule_is_paused(FULL_CONFIG_SCHEDULE_NAME)

        result = runner.invoke(resume, ["--name", FULL_CONFIG_SCHEDULE_NAME])
        assert result.exit_code == 0
        assert not fake_schedule_sdk.schedule_is_paused(FULL_CONFIG_SCHEDULE_NAME)

    def test_id(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        assert not fake_schedule_sdk.schedule_is_paused(fake_schedule_sdk.applied_id)

        result = runner.invoke(pause, ["--id", fake_schedule_sdk.applied_id])
        assert result.exit_code == 0
        assert fake_schedule_sdk.schedule_is_paused(fake_schedule_sdk.applied_id)

        result = runner.invoke(resume, ["--id", fake_schedule_sdk.applied_id])
        assert result.exit_code == 0
        assert not fake_schedule_sdk.schedule_is_paused(fake_schedule_sdk.applied_id)

    def test_config_file(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        assert not fake_schedule_sdk.schedule_is_paused(FULL_CONFIG_SCHEDULE_NAME)

        result = runner.invoke(pause, ["--config-file", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_schedule_sdk.schedule_is_paused(FULL_CONFIG_SCHEDULE_NAME)

        result = runner.invoke(resume, ["--config-file", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert not fake_schedule_sdk.schedule_is_paused(FULL_CONFIG_SCHEDULE_NAME)


class TestStatus:
    def test_no_identifiers(self, fake_schedule_sdk):
        runner = CliRunner()
        result = runner.invoke(status)
        _assert_error_message(
            result,
            message="One of '--name', '--id', or '--config-file' must be provided.",
        )

    @pytest.mark.parametrize(
        "identifiers",
        [
            ("name", "config_file", None),
            ("name", None, "id"),
            (None, "config_file", "id"),
            ("name", "config_file", "id"),
        ],
    )
    def test_multi_identifiers(self, identifiers, fake_schedule_sdk):
        runner = CliRunner()
        args = []
        name, config_file, id = identifiers  # noqa: A001
        if name:
            args += ["--name", name]
        if config_file:
            args += ["--config-file", config_file]
        if id:
            args += ["--id", id]

        result = runner.invoke(status, args)
        _assert_error_message(
            result,
            message="Only one of '--name', '--id', and '--config-file' can be provided.",
        )

    def test_name(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        result = runner.invoke(status, ["--name", FULL_CONFIG_SCHEDULE_NAME])
        assert result.exit_code == 0
        assert fake_schedule_sdk.applied_id in result.stdout
        assert fake_schedule_sdk.applied_name in result.stdout

    def test_id(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        result = runner.invoke(status, ["--id", fake_schedule_sdk.applied_id])
        assert result.exit_code == 0
        assert fake_schedule_sdk.applied_id in result.stdout
        assert fake_schedule_sdk.applied_name in result.stdout

    def test_config_file(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        result = runner.invoke(status, ["--config-file", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_schedule_sdk.applied_id in result.stdout
        assert fake_schedule_sdk.applied_name in result.stdout

    def test_verbose_flag(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])

        # No verbose flag -- exclude details
        result = runner.invoke(status, ["-f", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert "id" in result.stdout
        assert "name" in result.stdout
        assert "state" in result.stdout
        assert "config" not in result.stdout

        # Verbose flag -- include details
        result = runner.invoke(status, ["-f", FULL_CONFIG_PATH, "-v"])
        assert result.exit_code == 0
        assert "id" in result.stdout
        assert "name" in result.stdout
        assert "state" in result.stdout
        assert "config" in result.stdout


class TestTrigger:
    def test_no_identifiers(self, fake_schedule_sdk):
        runner = CliRunner()
        result = runner.invoke(trigger)
        _assert_error_message(
            result,
            message="One of '--name', '--id', or '--config-file' must be provided.",
        )

    @pytest.mark.parametrize(
        "identifiers",
        [
            ("name", "config_file", None),
            ("name", None, "id"),
            (None, "config_file", "id"),
            ("name", "config_file", "id"),
        ],
    )
    def test_multi_identifiers(self, identifiers, fake_schedule_sdk):
        runner = CliRunner()
        args = []
        name, config_file, id = identifiers  # noqa: A001
        if name:
            args += ["--name", name]
        if config_file:
            args += ["--config-file", config_file]
        if id:
            args += ["--id", id]

        result = runner.invoke(trigger, args)
        _assert_error_message(
            result,
            message="Only one of '--name', '--id', and '--config-file' can be provided.",
        )

    def test_name(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        result = runner.invoke(trigger, ["--name", FULL_CONFIG_SCHEDULE_NAME])
        assert result.exit_code == 0
        assert fake_schedule_sdk.trigger_counts(FULL_CONFIG_SCHEDULE_NAME) == 1

    def test_id(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        result = runner.invoke(trigger, ["--id", fake_schedule_sdk.applied_id])
        assert result.exit_code == 0
        assert fake_schedule_sdk.trigger_counts(fake_schedule_sdk.applied_id) == 1

    def test_config_file(self, fake_schedule_sdk):
        runner = CliRunner()
        runner.invoke(apply, ["-f", FULL_CONFIG_PATH])
        result = runner.invoke(trigger, ["--config-file", FULL_CONFIG_PATH])
        assert result.exit_code == 0
        assert fake_schedule_sdk.trigger_counts(FULL_CONFIG_SCHEDULE_NAME) == 1
