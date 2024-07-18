"""Entrypoint to generate reference docs for the Anyscale CLI/SDK.

Usage: python -m anyscale._private.docgen --help
"""
import os

import click

import anyscale
from anyscale._private.docgen.generator import MarkdownGenerator, Module
from anyscale.commands import (
    cloud_commands,
    compute_config_commands,
    image_commands,
    job_commands,
    logs_commands,
    schedule_commands,
    service_account_commands,
    service_commands,
)
from anyscale.compute_config.models import (
    ComputeConfig,
    ComputeConfigVersion,
    HeadNodeConfig,
    MarketType,
    WorkerNodeGroupConfig,
)
from anyscale.image.models import ImageBuild, ImageBuildStatus
from anyscale.job.models import (
    JobConfig,
    JobLogMode,
    JobRunState,
    JobRunStatus,
    JobState,
    JobStatus,
)
from anyscale.schedule.models import ScheduleConfig, ScheduleState, ScheduleStatus
from anyscale.service.models import (
    RayGCSExternalStorageConfig,
    ServiceConfig,
    ServiceState,
    ServiceStatus,
    ServiceVersionState,
    ServiceVersionStatus,
    TracingConfig,
)


# Defines all modules to be documented.
ALL_MODULES = [
    Module(
        title="Job",
        filename="job-api.md",
        cli_prefix="anyscale job",
        cli_commands=[
            job_commands.submit,
            job_commands.status,
            job_commands.terminate,
            job_commands.archive,
            job_commands.logs,
            job_commands.wait,
            job_commands.list,
        ],
        sdk_prefix="anyscale.job",
        sdk_commands=[
            anyscale.job.submit,
            anyscale.job.status,
            anyscale.job.terminate,
            anyscale.job.archive,
            anyscale.job.get_logs,
            anyscale.job.wait,
        ],
        models=[JobConfig, JobState, JobStatus, JobRunStatus, JobRunState, JobLogMode],
    ),
    Module(
        title="Schedule",
        filename="schedule-api.md",
        cli_prefix="anyscale schedule",
        cli_commands=[
            schedule_commands.create,
            schedule_commands.update,
            schedule_commands.apply,
            schedule_commands.list,
            schedule_commands.pause,
            schedule_commands.resume,
            schedule_commands.status,
            schedule_commands.trigger,
            schedule_commands.url,
        ],
        sdk_prefix="anyscale.schedule",
        sdk_commands=[
            anyscale.schedule.apply,
            anyscale.schedule.set_state,
            anyscale.schedule.status,
            anyscale.schedule.trigger,
        ],
        models=[ScheduleConfig, ScheduleState, ScheduleStatus],
    ),
    Module(
        title="Service",
        filename="service-api.md",
        cli_prefix="anyscale service",
        cli_commands=[
            service_commands.deploy,
            service_commands.status,
            service_commands.wait,
            service_commands.rollback,
            service_commands.terminate,
        ],
        sdk_prefix="anyscale.service",
        sdk_commands=[
            anyscale.service.deploy,
            anyscale.service.status,
            anyscale.service.wait,
            anyscale.service.rollback,
            anyscale.service.terminate,
        ],
        models=[
            ServiceConfig,
            RayGCSExternalStorageConfig,
            TracingConfig,
            ServiceStatus,
            ServiceState,
            ServiceVersionStatus,
            ServiceVersionState,
        ],
    ),
    Module(
        title="Compute Config",
        filename="compute-config-api.md",
        cli_prefix="anyscale compute-config",
        cli_commands=[
            compute_config_commands.create_compute_config,
            compute_config_commands.get_compute_config,
            compute_config_commands.archive_compute_config,
        ],
        sdk_prefix="anyscale.compute_config",
        sdk_commands=[
            anyscale.compute_config.create,
            anyscale.compute_config.get,
            anyscale.compute_config.archive,
        ],
        models=[
            ComputeConfig,
            HeadNodeConfig,
            WorkerNodeGroupConfig,
            MarketType,
            ComputeConfigVersion,
        ],
    ),
    Module(
        title="Service Account",
        filename="service-account.md",
        cli_prefix="anyscale service-account",
        cli_commands=[
            service_account_commands.create,
            service_account_commands.create_api_key,
            service_account_commands.list_service_accounts,
            service_account_commands.delete,
            service_account_commands.rotate_api_keys,
        ],
        sdk_prefix="anyscale.service_account",
        sdk_commands=[],
        models=[],
    ),
    Module(
        title="Image",
        filename="image.md",
        cli_prefix="anyscale image",
        cli_commands=[image_commands.build, image_commands.get,],
        sdk_prefix="anyscale.image",
        sdk_commands=[anyscale.image.build, anyscale.image.get,],
        models=[ImageBuild, ImageBuildStatus],
    ),
    Module(
        title="Cloud",
        filename="cloud.md",
        cli_prefix="anyscale cloud",
        cli_commands=[
            cloud_commands.setup_cloud,
            cloud_commands.register_cloud,
            cloud_commands.cloud_edit,
            cloud_commands.cloud_update,
            cloud_commands.cloud_delete,
            cloud_commands.cloud_verify,
            cloud_commands.list_cloud,
            cloud_commands.cloud_config_update,
        ],
        sdk_prefix="anyscale.cloud",
        sdk_commands=[],
        models=[],
        cli_command_group_prefix={cloud_commands.cloud_config_update: "config"},
    ),
    Module(
        title="Logs",
        filename="logs.md",
        cli_prefix="anyscale logs",
        cli_commands=[logs_commands.anyscale_logs_cluster],
        sdk_prefix="anyscale.logs",
        sdk_commands=[],
        models=[],
    ),
]


@click.command(help="Generate markdown docs for the Anyscale CLI & SDK.")
@click.argument("output_dir")
@click.option(
    "-r",
    "--remove-existing",
    is_flag=True,
    default=False,
    help="If set, all files in the 'output_dir' that were not generated will be removed.",
)
def generate(
    output_dir: str, *, remove_existing: bool = False,
):
    if not os.path.isdir(output_dir):
        raise RuntimeError(f"output_dir '{output_dir}' does not exist.")

    gen = MarkdownGenerator(ALL_MODULES)
    gen.generate()

    generated_files = set()
    os.makedirs(output_dir, exist_ok=True)
    for filename, content in gen.generate().items():
        generated_files.add(filename)
        full_path = os.path.join(output_dir, filename)
        print(f"Writing output file {full_path}")
        with open(full_path, "w") as f:
            f.write(content)

    if remove_existing:
        to_remove = set(os.listdir(output_dir)) - generated_files
        for path in to_remove:
            full_path = os.path.join(output_dir, path)
            print(f"Removing existing file {full_path}")
            os.unlink(full_path)


if __name__ == "__main__":
    generate()
