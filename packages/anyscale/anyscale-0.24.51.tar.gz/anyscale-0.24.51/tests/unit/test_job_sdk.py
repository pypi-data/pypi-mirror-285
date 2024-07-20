import copy
from dataclasses import dataclass, field
from datetime import datetime
import pathlib
import re
from typing import List, Optional, Tuple, Union
import uuid

from common import (
    MULTI_LINE_REQUIREMENTS,
    OPENAPI_NO_VALIDATION,
    RequirementsFile,
    SINGLE_LINE_REQUIREMENTS,
    TEST_COMPUTE_CONFIG_DICT,
    TEST_CONTAINERFILE,
    TEST_REQUIREMENTS_FILES,
    TestLogger,
)
import pytest

from anyscale import Anyscale
from anyscale._private.anyscale_client import (
    FakeAnyscaleClient,
    WORKSPACE_CLUSTER_NAME_PREFIX,
)
from anyscale._private.models.image_uri import ImageURI
from anyscale._private.sdk.timer import FakeTimer
from anyscale.client.openapi_client.models import (
    Cloud,
    ComputeTemplate,
    ComputeTemplateConfig,
    CreateInternalProductionJob,
    HaJobGoalStates,
    HaJobStates,
    InternalProductionJob,
    ProductionJobConfig,
    ProductionJobStateTransition,
)
from anyscale.client.openapi_client.models.job_status import (
    JobStatus as BackendJobStatus,
)
from anyscale.client.openapi_client.models.production_job import ProductionJob
from anyscale.client.openapi_client.models.ray_runtime_env_config import (
    RayRuntimeEnvConfig,
)
from anyscale.job import JobSDK
from anyscale.job.models import (
    JobConfig,
    JobLogMode,
    JobRunState,
    JobRunStatus,
    JobState,
    JobStatus,
)
from anyscale.sdk.anyscale_client.models.job import Job as APIJobRun
from anyscale.shared_anyscale_utils.latest_ray_version import LATEST_RAY_VERSION


@pytest.fixture()
def job_sdk_with_fakes(
    sdk_with_fakes: Tuple[Anyscale, FakeAnyscaleClient, TestLogger, FakeTimer]
) -> Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer]:
    sdk, client, logger, timer = sdk_with_fakes
    return sdk.job, client, logger, timer


class TestSubmit:
    def test_basic(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        config = JobConfig(entrypoint="python hello.py", name="test-job-name",)
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

    def test_default_name(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        config = JobConfig(entrypoint="python hello.py",)
        sdk.submit(config)
        assert fake_client.submitted_job.name
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name=fake_client.submitted_job.name,
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

    def test_custom_image_from_containerfile(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        fake_containerfile = pathlib.Path(TEST_CONTAINERFILE).read_text()
        job_name = "test-job-name"
        build_id = fake_client.get_cluster_env_build_id_from_containerfile(
            cluster_env_name=f"image-for-job-{job_name}",
            containerfile=fake_containerfile,
            anonymous=False,
        )

        config = JobConfig(
            entrypoint="python hello.py",
            name=job_name,
            containerfile=TEST_CONTAINERFILE,
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name=job_name,
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=build_id,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

    def test_custom_image_from_image_uri(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        job_name = "test-job-name"
        image_uri = ImageURI.from_str("docker.io/user/my-custom-image:latest")
        build_id = fake_client.get_cluster_env_build_id_from_image_uri(
            image_uri=image_uri, ray_version="2.23.0",
        )

        config = JobConfig(
            entrypoint="python hello.py",
            name=job_name,
            image_uri=str(image_uri),
            ray_version="2.23.0",
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name=job_name,
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=build_id,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )
        assert fake_client.submitted_job
        build_id = fake_client.submitted_job.config.build_id
        build = fake_client.get_cluster_env_build(build_id)
        assert build
        assert build.ray_version == "2.23.0"

        sdk.submit(
            config.options(image_uri="docker.io/user/does-not-exist:latest").options(
                ray_version=None
            )
        )
        assert fake_client.submitted_job
        new_build_id = fake_client.submitted_job.config.build_id
        new_build = fake_client.get_cluster_env_build(new_build_id)
        assert new_build
        assert new_build.docker_image_name == "docker.io/user/does-not-exist:latest"
        assert new_build.ray_version == LATEST_RAY_VERSION

    def test_custom_compute_config_name(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        fake_client.add_compute_config(
            ComputeTemplate(
                id="compute_id123",
                name="my-custom-compute-config",
                config=ComputeTemplateConfig(
                    cloud_id="test-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config = JobConfig(
            entrypoint="python hello.py",
            name="test-job-name",
            compute_config="my-custom-compute-config",
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id="compute_id123",
            ),
        )

        with pytest.raises(
            ValueError, match="The compute config 'does-not-exist' does not exist."
        ):
            sdk.submit(config.options(compute_config="does-not-exist"))

    def test_custom_compute_config_dict(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        fake_client.add_cloud(
            Cloud(
                id=str(uuid.uuid4()),
                name=TEST_COMPUTE_CONFIG_DICT["cloud"],
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
        )

        # Specify a compute config as a dictionary (anonymous).
        config = JobConfig(
            entrypoint="python hello.py",
            name="test-job-name",
            compute_config=TEST_COMPUTE_CONFIG_DICT,
        )
        sdk.submit(config)
        anonymous_compute_config_id = fake_client.submitted_job.config.compute_config_id
        anonymous_compute_config = fake_client.get_compute_config(
            anonymous_compute_config_id
        )
        assert anonymous_compute_config.anonymous
        assert anonymous_compute_config.id == anonymous_compute_config_id
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=anonymous_compute_config_id,
            ),
        )

        # Test an invalid dict.
        with pytest.raises(
            TypeError,
            match=re.escape("__init__() got an unexpected keyword argument 'bad'"),
        ):
            sdk.submit(
                JobConfig(
                    entrypoint="python hello.py",
                    name="test-job-name",
                    compute_config={"bad": "config"},
                )
            )

    def test_max_retries(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        config = JobConfig(
            entrypoint="python hello.py", name="test-job-name", max_retries=10,
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.DEFAULT_PROJECT_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=10,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

    def test_project(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        project = "test-project-name"
        project_id = fake_client.register_project_by_name(project)
        config = JobConfig(
            entrypoint="python hello.py", name="test-job-name", project=project,
        )
        sdk.submit(config)
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=project_id,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env=None,
                max_retries=1,
                build_id=fake_client.DEFAULT_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.DEFAULT_CLUSTER_COMPUTE_ID,
            ),
        )

        with pytest.raises(
            ValueError,
            match="Cloud does not match from provided `cloud` and `compute_config`. Either pass one of these or ensure they match.",
        ):
            fake_client.add_cloud(
                Cloud(
                    id=str(uuid.uuid4()),
                    name=TEST_COMPUTE_CONFIG_DICT["cloud"],
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
            )
            config = JobConfig(
                entrypoint="python hello.py",
                name="test-job-name",
                compute_config=TEST_COMPUTE_CONFIG_DICT,
                cloud=fake_client.DEFAULT_CLOUD_NAME,
            )
            sdk.submit(config)


class TestDeployWorkspaceDefaults:
    def test_name_defaults_to_workspace_name(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        # Happy path: workspace cluster name has the expected prefix.
        fake_client.set_inside_workspace(
            True,
            cluster_name=WORKSPACE_CLUSTER_NAME_PREFIX + "super-special-workspace-name",
        )
        sdk.submit(JobConfig(entrypoint="python hello.py"))
        assert fake_client.submitted_job.name == "job-super-special-workspace-name"

        # Defensive path: workspace cluster name doesn't have the expected prefix.
        fake_client.set_inside_workspace(
            True, cluster_name="not-sure-how-this-happened"
        )
        sdk.submit(JobConfig(entrypoint="python hello.py"))
        assert fake_client.submitted_job.name == "job-not-sure-how-this-happened"

    def test_pick_up_cluster_configs(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        fake_client.set_inside_workspace(True)

        fake_client.add_compute_config(
            ComputeTemplate(
                id=fake_client.WORKSPACE_CLUSTER_COMPUTE_ID,
                config=ComputeTemplateConfig(
                    cloud_id=fake_client.WORKSPACE_CLOUD_ID,
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        sdk.submit(
            JobConfig(
                entrypoint="python hello.py",
                name="test-job-name",
                working_dir="s3://remote.zip",
            )
        )
        assert fake_client.submitted_job == CreateInternalProductionJob(
            name="test-job-name",
            project_id=fake_client.WORKSPACE_PROJECT_ID,
            workspace_id=fake_client.WORKSPACE_ID,
            config=ProductionJobConfig(
                entrypoint="python hello.py",
                runtime_env={"working_dir": "s3://remote.zip"},
                max_retries=1,
                build_id=fake_client.WORKSPACE_CLUSTER_ENV_BUILD_ID,
                compute_config_id=fake_client.WORKSPACE_CLUSTER_COMPUTE_ID,
            ),
        )


class TestOverrideApplicationRuntimeEnvs:
    @pytest.mark.parametrize(
        "new_py_modules", [None, [], ["A"], ["C", "D"]],
    )
    def test_update_py_modules(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        new_py_modules: Optional[List[str]],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        job = JobConfig(
            name="test-job-name",
            entrypoint="python hello.py",
            py_modules=new_py_modules,
        )

        sdk.submit(job)
        submitted_runtime_env = fake_client.submitted_job.config.runtime_env
        if new_py_modules:
            uploaded_py_modules = [
                fake_client._upload_uri_mapping[local_dir]
                for local_dir in new_py_modules
            ]
        else:
            uploaded_py_modules = None

        if uploaded_py_modules:
            assert submitted_runtime_env.get("py_modules") == uploaded_py_modules
        else:
            assert (
                submitted_runtime_env is None
                or "py_modules" not in submitted_runtime_env
            )

    @pytest.mark.parametrize("excludes_override", [None, ["override"]])
    @pytest.mark.parametrize(
        "working_dir_override", [None, "./some-local-path", "s3://some-remote-path.zip"]
    )
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_override_working_dir_excludes(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        inside_workspace: bool,
        working_dir_override: Optional[str],
        excludes_override: Optional[List[str]],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        fake_client.set_inside_workspace(inside_workspace)

        job = JobConfig(
            name="test-job-name",
            entrypoint="python hello.py",
            working_dir=working_dir_override,
            excludes=excludes_override,
        )

        sdk.submit(job)
        submitted_runtime_env = fake_client.submitted_job.config.runtime_env

        cloud_id = (
            FakeAnyscaleClient.WORKSPACE_CLOUD_ID
            if inside_workspace
            else FakeAnyscaleClient.DEFAULT_CLOUD_ID
        )
        cwd_uri = fake_client.upload_local_dir_to_cloud_storage(".", cloud_id=cloud_id)
        if working_dir_override is None and not inside_workspace:
            assert (
                submitted_runtime_env is None
                or "working_dir" not in submitted_runtime_env
            )
        elif working_dir_override is None and inside_workspace:
            assert submitted_runtime_env["working_dir"] == cwd_uri
        elif working_dir_override is not None and working_dir_override.startswith("s3"):
            assert submitted_runtime_env["working_dir"] == working_dir_override
        else:
            fake_client.upload_local_dir_to_cloud_storage(
                "./some-local-path", cloud_id=cloud_id
            )

        if excludes_override is None:
            assert (
                submitted_runtime_env is None or "excludes" not in submitted_runtime_env
            )
        else:
            assert submitted_runtime_env["excludes"] == ["override"]

    @pytest.mark.parametrize(
        "requirements_override",
        [None, MULTI_LINE_REQUIREMENTS.get_path(), ["override"]],
    )
    @pytest.mark.parametrize("workspace_tracking_enabled", [False, True])
    @pytest.mark.parametrize(
        "enable_image_build_for_tracked_requirements", [False, True]
    )
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_override_requirements(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        inside_workspace: bool,
        workspace_tracking_enabled: bool,
        enable_image_build_for_tracked_requirements: bool,
        requirements_override: Union[None, str, List[str]],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        sdk._private_sdk._image_sdk._enable_image_build_for_tracked_requirements = (
            enable_image_build_for_tracked_requirements
        )
        fake_client.set_inside_workspace(
            inside_workspace,
            requirements_path=SINGLE_LINE_REQUIREMENTS.get_path()
            if workspace_tracking_enabled
            else None,
        )

        job = JobConfig(
            name="test-job-name",
            entrypoint="python hello.py",
            requirements=requirements_override,
        )

        sdk.submit(job)
        if (
            inside_workspace
            and workspace_tracking_enabled
            and enable_image_build_for_tracked_requirements
        ):
            build_id = fake_client.submitted_job.config.build_id
            assert build_id
            build = fake_client.get_cluster_env_build(build_id)
            assert build.containerfile == (
                "# syntax=docker/dockerfile:1\n"
                "FROM docker.io/my/base-ws-image:latest\n"
                'RUN pip install "pip-install-test"'
            )
        submitted_runtime_env = fake_client.submitted_job.config.runtime_env

        if isinstance(requirements_override, str):
            # Override with a file.
            pass
        elif isinstance(requirements_override, list):
            # Override with a list.
            pass
        elif (
            inside_workspace
            and workspace_tracking_enabled
            and not enable_image_build_for_tracked_requirements
        ):
            # Workspace default.
            expected_workspace_pip = SINGLE_LINE_REQUIREMENTS.expected_pip_list
            assert submitted_runtime_env["pip"] == expected_workspace_pip
        else:
            # No overrides.
            assert submitted_runtime_env is None or "pip" not in submitted_runtime_env


class TestDeployUploadDirs:
    @pytest.mark.parametrize("inside_workspace", [False, True])
    def test_upload_basic_working_dir(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        inside_workspace: bool,
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        fake_client.set_inside_workspace(inside_workspace)

        config = JobConfig(entrypoint="python test.py", working_dir=".",)
        original_config = copy.deepcopy(config)

        sdk.submit(config)
        # The original config should not be modified.
        assert config == original_config

        # Check that the correct cloud_id was used for the upload.
        expected_cloud_id = (
            FakeAnyscaleClient.WORKSPACE_CLOUD_ID
            if inside_workspace
            else FakeAnyscaleClient.DEFAULT_CLOUD_ID
        )
        assert fake_client.submitted_job.config.runtime_env["working_dir"].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(cloud_id=expected_cloud_id)
        )

    def test_upload_uses_cloud_from_compute_config(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        fake_client.add_compute_config(
            ComputeTemplate(
                id="fake-compute-config-id",
                name="fake-compute-config",
                config=ComputeTemplateConfig(
                    cloud_id="compute-config-cloud-id",
                    local_vars_configuration=OPENAPI_NO_VALIDATION,
                ),
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )
        )

        config = JobConfig(
            entrypoint="python test.py",
            working_dir=".",
            compute_config="fake-compute-config",
        )
        sdk.submit(config)

        # Check that the correct cloud_id was used for the upload.
        expected_cloud_id = "compute-config-cloud-id"
        assert fake_client.submitted_job.config.runtime_env["working_dir"].startswith(
            FakeAnyscaleClient.CLOUD_BUCKET.format(cloud_id=expected_cloud_id)
        )

    def test_upload_with_no_local_dirs(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        """Configs should be left unchanged if there are no local dirs."""
        sdk, fake_client, _, _ = job_sdk_with_fakes

        basic_config = JobConfig(entrypoint="python test.py",)
        sdk.submit(basic_config)
        assert fake_client.submitted_job.config.runtime_env is None

        config_with_requirements = JobConfig(
            entrypoint="python test.py", requirements=["pip-install-test"],
        )
        sdk.submit(config_with_requirements)
        assert fake_client.submitted_job.config.runtime_env == {
            "pip": ["pip-install-test"]
        }

    def test_no_upload_remote_working_dir(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        config = JobConfig(
            entrypoint="python test.py", working_dir="s3://some-remote-uri.zip",
        )

        sdk.submit(config)
        assert (
            fake_client.submitted_job.config.runtime_env["working_dir"]
            == "s3://some-remote-uri.zip"
        )


class TestLoadRequirementsFiles:
    @pytest.mark.parametrize("requirements", [None, *TEST_REQUIREMENTS_FILES])
    def test_override_requirements_file(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        requirements: Optional[RequirementsFile],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        job = JobConfig(entrypoint="python hello.py")
        if requirements is not None:
            job = job.options(requirements=requirements.get_path())

        if requirements is not None and requirements.expected_pip_list is None:
            with pytest.raises(FileNotFoundError):
                sdk.submit(job)

            return
        else:
            sdk.submit(job)

        if requirements is None:
            assert fake_client.submitted_job.config.runtime_env is None
        else:
            assert (
                fake_client.submitted_job.config.runtime_env["pip"]
                == requirements.expected_pip_list
            )


TEST_JOB_ID = "test-job-id"
TEST_JOB_NAME = "test-job-name"
TEST_COMPUTE_CONFIG_NAME = "fake-compute-config"
OTHER_COMPUTE_CONFIG_NAME = "other-compute-config"
TEST_COMPUTE_CONFIG_ID = "fake-compute-config-id"


DEFAULT_PROD_COMPUTE_CONFIG = ComputeTemplate(
    id=FakeAnyscaleClient.DEFAULT_CLUSTER_COMPUTE_ID,
    name=TEST_COMPUTE_CONFIG_NAME,
    config=ComputeTemplateConfig(
        cloud_id="compute-config-cloud-id",
        local_vars_configuration=OPENAPI_NO_VALIDATION,
    ),
    local_vars_configuration=OPENAPI_NO_VALIDATION,
)


OTHER_PROD_COMPUTE_CONFIG = ComputeTemplate(
    id=FakeAnyscaleClient.DEFAULT_CLUSTER_COMPUTE_ID,
    name=OTHER_COMPUTE_CONFIG_NAME,
    config=ComputeTemplateConfig(
        cloud_id="other-compute-config-cloud-id",
        local_vars_configuration=OPENAPI_NO_VALIDATION,
    ),
    local_vars_configuration=OPENAPI_NO_VALIDATION,
)

DEFAULT_PROD_JOB_CONFIG = ProductionJobConfig(
    entrypoint="python hello.py",
    runtime_env=None,
    max_retries=1,
    build_id=FakeAnyscaleClient.DEFAULT_CLUSTER_ENV_BUILD_ID,
    compute_config_id=FakeAnyscaleClient.DEFAULT_CLUSTER_COMPUTE_ID,
)


DEFAULT_EXPECTED_JOB_CONFIG = JobConfig(
    name=TEST_JOB_NAME,
    entrypoint="python hello.py",
    compute_config=TEST_COMPUTE_CONFIG_NAME + ":1",
)

DEFAULT_EXPECTED_STATUS = JobStatus(
    id=TEST_JOB_ID,
    name=TEST_JOB_NAME,
    state=JobState.UNKNOWN,
    config=DEFAULT_EXPECTED_JOB_CONFIG,
    runs=[],
)

DEFAULT_JOB_RUN = APIJobRun(
    id="job-run-id",
    ray_session_name="job-run-ray-session-id",
    ray_job_id="job-run-ray-job-id",
    status=BackendJobStatus.SUCCEEDED,
    created_at=datetime.now(),
    cluster_id="job-run-cluster-id",
    runtime_environment_id="job-run-runtime-environment-id",
    creator_id="job-run-creator-id",
    name="job-run-name",
)

DEFAULT_JOB_RUN_STATUS = JobRunStatus(
    name=DEFAULT_JOB_RUN.name, state=JobRunState.SUCCEEDED
)


def _expected_status(**kwargs) -> JobStatus:
    return JobStatus(
        id=kwargs["id"] if "id" in kwargs else DEFAULT_EXPECTED_STATUS.id,
        name=kwargs["name"] if "name" in kwargs else DEFAULT_EXPECTED_STATUS.name,
        state=kwargs["state"] if "state" in kwargs else DEFAULT_EXPECTED_STATUS.state,
        config=kwargs["config"]
        if "config" in kwargs
        else DEFAULT_EXPECTED_STATUS.config,
        runs=kwargs["runs"] if "runs" in kwargs else DEFAULT_EXPECTED_STATUS.runs,
    )


def _job_run(**kwargs) -> APIJobRun:
    return APIJobRun(
        id=kwargs["id"] if "id" in kwargs else DEFAULT_JOB_RUN.id,
        ray_session_name=kwargs["ray_session_name"]
        if "ray_session_name" in kwargs
        else DEFAULT_JOB_RUN.ray_session_name,
        ray_job_id=kwargs["ray_job_id"]
        if "ray_job_id" in kwargs
        else DEFAULT_JOB_RUN.ray_job_id,
        status=kwargs["status"] if "status" in kwargs else DEFAULT_JOB_RUN.status,
        created_at=kwargs["created_at"]
        if "created_at" in kwargs
        else DEFAULT_JOB_RUN.created_at,
        cluster_id=kwargs["cluster_id"]
        if "cluster_id" in kwargs
        else DEFAULT_JOB_RUN.cluster_id,
        runtime_environment_id=kwargs["runtime_environment_id"]
        if "runtime_environment_id" in kwargs
        else DEFAULT_JOB_RUN.runtime_environment_id,
        creator_id=kwargs["creator_id"]
        if "creator_id" in kwargs
        else DEFAULT_JOB_RUN.creator_id,
        name=kwargs["name"] if "name" in kwargs else DEFAULT_JOB_RUN.name,
    )


def _job_run_status(**kwargs) -> JobRunStatus:
    return JobRunStatus(
        name=kwargs["name"] if "name" in kwargs else DEFAULT_JOB_RUN_STATUS.name,
        state=kwargs["state"] if "state" in kwargs else DEFAULT_JOB_RUN_STATUS.state,
    )


@dataclass
class JobStatusTestCase:
    id: str = TEST_JOB_ID
    name: str = TEST_JOB_NAME
    state: Optional[HaJobStates] = None
    compute_config: ComputeTemplate = DEFAULT_PROD_COMPUTE_CONFIG
    prod_job_config: ProductionJobConfig = DEFAULT_PROD_JOB_CONFIG
    expected_status: JobStatus = DEFAULT_EXPECTED_STATUS
    runs: List[APIJobRun] = field(default_factory=list)

    def job_model(self) -> ProductionJob:
        return InternalProductionJob(
            id=self.id,
            name=self.name,
            config=self.prod_job_config,
            state=ProductionJobStateTransition(
                current_state=self.state,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )


JOB_STATUS_TEST_CASES = [
    JobStatusTestCase(),
    JobStatusTestCase(
        state=HaJobStates.UPDATING,
        expected_status=_expected_status(state=JobState.RUNNING,),
    ),
    JobStatusTestCase(
        state=HaJobStates.RUNNING,
        expected_status=_expected_status(state=JobState.RUNNING,),
    ),
    JobStatusTestCase(
        state=HaJobStates.RESTARTING,
        expected_status=_expected_status(state=JobState.RUNNING,),
    ),
    JobStatusTestCase(
        state=HaJobStates.CLEANING_UP,
        expected_status=_expected_status(state=JobState.RUNNING,),
    ),
    JobStatusTestCase(
        state=HaJobStates.PENDING,
        expected_status=_expected_status(state=JobState.STARTING,),
    ),
    JobStatusTestCase(
        state=HaJobStates.AWAITING_CLUSTER_START,
        expected_status=_expected_status(state=JobState.STARTING),
    ),
    JobStatusTestCase(
        state=HaJobStates.SUCCESS,
        expected_status=_expected_status(state=JobState.SUCCEEDED,),
    ),
    JobStatusTestCase(
        state=HaJobStates.ERRORED,
        expected_status=_expected_status(state=JobState.FAILED,),
    ),
    JobStatusTestCase(
        state=HaJobStates.TERMINATED,
        expected_status=_expected_status(state=JobState.FAILED,),
    ),
    JobStatusTestCase(
        state=HaJobStates.BROKEN,
        expected_status=_expected_status(state=JobState.FAILED,),
    ),
    JobStatusTestCase(
        state=HaJobStates.OUT_OF_RETRIES,
        expected_status=_expected_status(state=JobState.FAILED),
    ),
    JobStatusTestCase(
        state=HaJobStates.SUCCESS,
        prod_job_config=ProductionJobConfig(
            entrypoint="python hello.py",
            runtime_env=RayRuntimeEnvConfig(
                working_dir="/usr/my_working_dir",
                pip=["package1", "package2"],
                env_vars={"ENV_VAR": "ENV_VAR_VALUE"},
            ),
            max_retries=1,
            build_id=FakeAnyscaleClient.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config_id=FakeAnyscaleClient.DEFAULT_CLUSTER_COMPUTE_ID,
        ),
        expected_status=JobStatus(
            id=TEST_JOB_ID,
            name=TEST_JOB_NAME,
            state=JobState.SUCCEEDED,
            config=JobConfig(
                name=TEST_JOB_NAME,
                entrypoint="python hello.py",
                working_dir="/usr/my_working_dir",
                requirements=["package1", "package2"],
                env_vars={"ENV_VAR": "ENV_VAR_VALUE"},
                compute_config=TEST_COMPUTE_CONFIG_NAME + ":1",
            ),
            runs=[],
        ),
    ),
    JobStatusTestCase(
        state=HaJobStates.SUCCESS,
        compute_config=OTHER_PROD_COMPUTE_CONFIG,
        prod_job_config=ProductionJobConfig(
            entrypoint="python hello.py",
            max_retries=1,
            build_id=FakeAnyscaleClient.DEFAULT_CLUSTER_ENV_BUILD_ID,
            compute_config=OTHER_PROD_COMPUTE_CONFIG,
            compute_config_id=FakeAnyscaleClient.DEFAULT_CLUSTER_COMPUTE_ID,
        ),
        expected_status=JobStatus(
            id=TEST_JOB_ID,
            name=TEST_JOB_NAME,
            state=JobState.SUCCEEDED,
            config=JobConfig(
                name=TEST_JOB_NAME,
                entrypoint="python hello.py",
                compute_config=OTHER_COMPUTE_CONFIG_NAME + ":1",
            ),
            runs=[],
        ),
    ),
    JobStatusTestCase(
        state=HaJobStates.SUCCESS,
        runs=[_job_run()],
        expected_status=_expected_status(
            state=JobState.SUCCEEDED, runs=[_job_run_status()]
        ),
    ),
    JobStatusTestCase(
        state=HaJobStates.ERRORED,
        runs=[_job_run(status=BackendJobStatus.FAILED)],
        expected_status=_expected_status(
            state=JobState.FAILED, runs=[_job_run_status(state=JobRunState.FAILED)]
        ),
    ),
    JobStatusTestCase(
        state=HaJobStates.SUCCESS,
        runs=[
            _job_run(status=BackendJobStatus.FAILED, name="failed-job-run"),
            _job_run(status=BackendJobStatus.SUCCEEDED, name="succeeded-job-run"),
        ],
        expected_status=_expected_status(
            state=JobState.SUCCEEDED,
            runs=[
                _job_run_status(state=JobRunState.FAILED, name="failed-job-run"),
                _job_run_status(state=JobRunState.SUCCEEDED, name="succeeded-job-run"),
            ],
        ),
    ),
]


class TestStatus:
    def test_job_not_found(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, _, _, _ = job_sdk_with_fakes

        with pytest.raises(
            RuntimeError, match="Job with name 'test-job-name' was not found."
        ):
            sdk.status(name="test-job-name")

    @pytest.mark.parametrize("test_case", JOB_STATUS_TEST_CASES)
    def test_build_status_from_model(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
        test_case: JobStatusTestCase,
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        fake_client.add_compute_config(test_case.compute_config)

        prod_job: ProductionJob = test_case.job_model()
        fake_client.update_job(prod_job)

        for run in test_case.runs:
            fake_client.update_job_run(prod_job_id=prod_job.id, model=run)

        status: JobStatus = sdk.status(name=prod_job.name)
        assert status == test_case.expected_status

        status = sdk.status(id=prod_job.id)
        assert status == test_case.expected_status

    def test_status_with_projects(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes

        project = "test-project-name"
        name = "test-job-name"
        cloud = "fake-default-cloud"
        fake_client.register_project_by_name(name=project, cloud="fake-default-cloud")

        fake_client.add_compute_config(DEFAULT_PROD_COMPUTE_CONFIG)

        job_id = sdk.submit(
            JobConfig(
                entrypoint="python hello.py", name=name, cloud=cloud, project=project,
            )
        )

        # submit another job with jobthe same name, under the default project
        sdk.submit(JobConfig(entrypoint="python hello.py", cloud=cloud, name=name))

        # ensure that the project filter works
        status: JobStatus = sdk.status(name=name, cloud=cloud, project=project)
        assert status.id == job_id
        assert status.config.project == project


class TestTerminate:
    def test_not_found(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, _, _, _ = job_sdk_with_fakes

        with pytest.raises(
            RuntimeError, match="Job with name 'does-not-exist' was not found"
        ):
            sdk.terminate(name="does-not-exist")

        with pytest.raises(
            RuntimeError, match="Job with ID 'does-not-exist' was not found"
        ):
            sdk.terminate(id="does-not-exist")

    @pytest.mark.parametrize("terminate_by_name", [True, False])
    def test_basic(
        self,
        terminate_by_name,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        job_id = "test-terminate-job-id"
        name = "test-terminate-job-name"
        prod_job: ProductionJob = InternalProductionJob(
            id=job_id,
            name=name,
            config=DEFAULT_PROD_JOB_CONFIG,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.RUNNING,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        fake_client.update_job(prod_job)

        if terminate_by_name:
            sdk.terminate(name=name)
        else:
            sdk.terminate(id=job_id)

        job: Optional[ProductionJob] = fake_client.get_job(
            job_id=job_id, name=None, cloud=None, project=None
        )
        assert job is not None and job.state == HaJobStates.TERMINATED


class TestArchive:
    def test_not_found(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, _, _, _ = job_sdk_with_fakes

        with pytest.raises(
            RuntimeError, match="Job with name 'does-not-exist' was not found"
        ):
            sdk.archive(name="does-not-exist")

        with pytest.raises(
            RuntimeError, match="Job with ID 'does-not-exist' was not found"
        ):
            sdk.archive(id="does-not-exist")

    @pytest.mark.parametrize("archive_by_name", [True, False])
    def test_basic(
        self,
        archive_by_name,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        job_id = "test-terminate-job-id"
        name = "test-terminate-job-name"
        prod_job: ProductionJob = InternalProductionJob(
            id=job_id,
            name=name,
            config=DEFAULT_PROD_JOB_CONFIG,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.SUCCESS,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        fake_client.update_job(prod_job)

        assert not fake_client.is_archived_job(job_id)

        if archive_by_name:
            sdk.archive(name=name)
        else:
            sdk.archive(id=job_id)

        assert fake_client.is_archived_job(job_id)


class TestWait:
    def test_job_not_found(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, _, _, _ = job_sdk_with_fakes
        with pytest.raises(
            RuntimeError, match="Job with name 'test-job-name' was not found."
        ):
            sdk.wait(
                name="test-job-name", state=JobState.SUCCEEDED, timeout_s=60,
            )

    def test_succeeds_immediately(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, logger, _ = job_sdk_with_fakes
        job_id = "test-wait-job-id"
        name = "test-wait-job-name"
        prod_job: ProductionJob = InternalProductionJob(
            id=job_id,
            name=name,
            config=DEFAULT_PROD_JOB_CONFIG,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.SUCCESS,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        fake_client.update_job(prod_job)

        sdk.wait(
            name=name, state=JobState.SUCCEEDED, timeout_s=60,
        )
        assert any(
            f"Job '{name}' reached target state, exiting" in info_log
            for info_log in logger.info_messages
        )

    def test_times_out(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, logger, _ = job_sdk_with_fakes
        job_id = "test-wait-job-id"
        name = "test-wait-job-name"
        prod_job: ProductionJob = InternalProductionJob(
            id=job_id,
            name=name,
            config=DEFAULT_PROD_JOB_CONFIG,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.RUNNING,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        fake_client.update_job(prod_job)

        with pytest.raises(
            TimeoutError,
            match=f"Job '{name}' did not reach target state SUCCEEDED within 60s. Last seen state: RUNNING.",
        ):
            sdk.wait(
                name=name, state=JobState.SUCCEEDED, timeout_s=60,
            )

    def test_job_run_sequence(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, logger, timer = job_sdk_with_fakes

        job_id = "test-wait-job-id"
        name = "test-wait-job-name"
        base_prod_job: ProductionJob = InternalProductionJob(
            id=job_id,
            name=name,
            config=DEFAULT_PROD_JOB_CONFIG,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.PENDING,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
        )
        fake_client.update_job(base_prod_job)

        def state_from_hajobstate(state) -> ProductionJobStateTransition:
            return ProductionJobStateTransition(
                current_state=state,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            )

        def start_sequence(i: int):
            model = copy.deepcopy(base_prod_job)
            if i == 0:
                model.state = state_from_hajobstate(HaJobStates.PENDING)
            elif i == 1:
                model.state = state_from_hajobstate(HaJobStates.RUNNING)
            else:
                model.state = state_from_hajobstate(HaJobStates.SUCCESS)

            fake_client.update_job(model)

        timer.set_on_poll_iteration(start_sequence)

        sdk.wait(
            name=name, state=JobState.SUCCEEDED, timeout_s=60,
        )

        assert any(
            f"Job '{name}' transitioned from STARTING to RUNNING" in info_log
            for info_log in logger.info_messages
        )
        assert any(
            f"Job '{name}' transitioned from RUNNING to SUCCEEDED" in info_log
            for info_log in logger.info_messages
        )
        assert any(
            f"Job '{name}' reached target state, exiting" in info_log
            for info_log in logger.info_messages
        )


class TestLogs:
    def test_not_found(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, _, _, _ = job_sdk_with_fakes

        with pytest.raises(
            RuntimeError, match="Job with name 'does-not-exist' was not found"
        ):
            sdk.get_logs(name="does-not-exist")

        with pytest.raises(
            RuntimeError, match="Job with ID 'does-not-exist' was not found"
        ):
            sdk.get_logs(id="does-not-exist")

    def test_errors_for_max_lines(
        self,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, _, _, _ = job_sdk_with_fakes

        with pytest.raises(TypeError, match="max_lines must be an int"):
            sdk.get_logs(name="name", max_lines="123")

        with pytest.raises(ValueError, match="max_lines must be > 0"):
            sdk.get_logs(name="name", max_lines=-123)

    @pytest.mark.parametrize("get_logs_by_name", [True, False])
    def test_basic(
        self,
        get_logs_by_name,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        job_id = "test-logs-job-id"
        name = "test-logs-job-name"

        failed_run = _job_run(
            id="failed_job_run_id",
            status=BackendJobStatus.FAILED,
            name="failed_job_run_name",
        )
        failed_run_logs = "JOB FAILED"
        fake_client.update_job_run(prod_job_id=job_id, model=failed_run)
        fake_client.add_job_run_logs(failed_run.id, failed_run_logs)

        prod_job: ProductionJob = InternalProductionJob(
            id=job_id,
            name=name,
            config=DEFAULT_PROD_JOB_CONFIG,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.SUCCESS,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
            last_job_run_id=failed_run.id,
        )
        fake_client.update_job(prod_job)

        logs = sdk.get_logs(name=name) if get_logs_by_name else sdk.get_logs(id=job_id)
        assert logs == failed_run_logs

        succeeded_run = _job_run(
            id="succeeded_job_run_id",
            status=BackendJobStatus.SUCCEEDED,
            name="succeeded_job_run_name",
        )
        succeeded_run_logs = "JOB SUCCEEDED"
        fake_client.update_job_run(prod_job_id=prod_job.id, model=succeeded_run)
        fake_client.add_job_run_logs(succeeded_run.id, succeeded_run_logs)

        prod_job.last_job_run_id = succeeded_run.id
        fake_client.update_job(prod_job)

        # without run arg gets latest job run logs
        logs = sdk.get_logs(name=name) if get_logs_by_name else sdk.get_logs(id=job_id)
        assert logs == succeeded_run_logs

        # grab by run name for both job runs
        logs = (
            sdk.get_logs(name=name, run=failed_run.name)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, run=failed_run.name)
        )
        assert logs == failed_run_logs

        logs = (
            sdk.get_logs(name=name, run=succeeded_run.name)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, run=succeeded_run.name)
        )
        assert logs == succeeded_run_logs

    @pytest.mark.parametrize("get_logs_by_name", [True, False])
    def test_head_and_tail_logs(
        self,
        get_logs_by_name: bool,
        job_sdk_with_fakes: Tuple[JobSDK, FakeAnyscaleClient, TestLogger, FakeTimer],
    ):
        sdk, fake_client, _, _ = job_sdk_with_fakes
        job_id = "test-logs-job-id"
        name = "test-logs-job-name"

        run = _job_run(
            id="job_run_id", status=BackendJobStatus.SUCCEEDED, name="job_run_name",
        )
        run_logs_lines = [f"Line {i}" for i in range(100)]
        fake_client.update_job_run(prod_job_id=job_id, model=run)
        fake_client.add_job_run_logs(run.id, "\n".join(run_logs_lines))

        prod_job: ProductionJob = InternalProductionJob(
            id=job_id,
            name=name,
            config=DEFAULT_PROD_JOB_CONFIG,
            state=ProductionJobStateTransition(
                current_state=HaJobStates.SUCCESS,
                goal_state=HaJobGoalStates.SUCCESS,
                local_vars_configuration=OPENAPI_NO_VALIDATION,
            ),
            local_vars_configuration=OPENAPI_NO_VALIDATION,
            last_job_run_id=run.id,
        )
        fake_client.update_job(prod_job)

        # using head to limit the number of logs
        num_lines = 5
        logs = (
            sdk.get_logs(name=name, mode=JobLogMode.HEAD, max_lines=num_lines)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, mode=JobLogMode.HEAD, max_lines=num_lines)
        )
        assert logs == "\n".join(run_logs_lines[:num_lines])

        # using tail to limit the number of logs
        logs = (
            sdk.get_logs(name=name, mode=JobLogMode.TAIL, max_lines=num_lines)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, mode=JobLogMode.TAIL, max_lines=num_lines)
        )
        assert logs == "\n".join(run_logs_lines[-1 * num_lines :])

        # defaults to tailing if mode is not passed
        logs = (
            sdk.get_logs(name=name, max_lines=num_lines)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, max_lines=num_lines)
        )
        assert logs == "\n".join(run_logs_lines[-1 * num_lines :])

        # using strings instead of JobLogMode
        logs = (
            sdk.get_logs(name=name, mode="HEAD", max_lines=num_lines)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, mode="HEAD", max_lines=num_lines)
        )
        assert logs == "\n".join(run_logs_lines[:num_lines])

        logs = (
            sdk.get_logs(name=name, mode="TAIL", max_lines=num_lines)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, mode="TAIL", max_lines=num_lines)
        )
        assert logs == "\n".join(run_logs_lines[-1 * num_lines :])

        # passing max_lines greater than number of lines for both head or tail fetches whole log
        num_lines = 1000
        logs = (
            sdk.get_logs(name=name, mode=JobLogMode.HEAD, max_lines=num_lines)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, mode=JobLogMode.HEAD, max_lines=num_lines)
        )
        assert logs == "\n".join(run_logs_lines)

        logs = (
            sdk.get_logs(name=name, mode=JobLogMode.TAIL, max_lines=num_lines)
            if get_logs_by_name
            else sdk.get_logs(id=job_id, mode=JobLogMode.TAIL, max_lines=num_lines)
        )
        assert logs == "\n".join(run_logs_lines)
