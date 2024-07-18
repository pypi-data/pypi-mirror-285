from typing import Optional

import click

import anyscale


@click.group("dataset", help="Dataset files stored on your Anyscale cloud.")
def dataset_cli():
    pass


@dataset_cli.command(
    name="upload", short_help="Upload a dataset to your Anyscale cloud.",
)
@click.argument("dataset_file", required=True)
@click.option(
    "--existing-dataset-id-or-name",
    "-d",
    required=False,
    help="ID or name of an existing dataset to upload a new version of. "
    "If not provided, a new dataset will be created.",
)
@click.option(
    "--description",
    required=False,
    help="Description of the dataset (or dataset version).",
)
@click.option(
    "--cloud-id",
    required=False,
    help="ID of the Anyscale cloud to upload a new dataset to. "
    "If not provided, the default Anyscale Hosted cloud will be used.",
)
@click.option(
    "--project-id",
    required=False,
    help="ID of the Anyscale project to upload a new dataset to. "
    "If not provided, the default project of the cloud will be used.",
)
def upload_dataset(
    dataset_file: str,
    existing_dataset_id_or_name: Optional[str],
    description: Optional[str],
    cloud_id: Optional[str],
    project_id: Optional[str],
):
    """
    Uploads a dataset, or a new version of a dataset, to your Anyscale cloud.

    DATASET_FILE = Path to the dataset file to upload

    Example usage:

        anyscale llm dataset upload path/to/my_dataset.jsonl

        anyscale llm dataset upload my_dataset2.jsonl -d my_dataset.jsonl

        anyscale llm dataset upload my_dataset2.jsonl -d file_123 --description 'added 3 lines'

    \b
    NOTE:
    If you are uploading a new version, have run this from within an Anyscale workspace,
    and neither `--cloud-id` nor `--project-id` is provided, the cloud and project of the workspace will be used.
    """
    anyscale.llm.dataset.upload(
        dataset_file,
        existing_dataset_id_or_name,
        description=description,
        cloud_id=cloud_id,
        project_id=project_id,
    )


@dataset_cli.command(
    name="download", short_help="Download a dataset.",
)
@click.argument(
    "dataset_id_or_name", required=True,
)
@click.option(
    "--version",
    "-v",
    required=False,
    type=int,
    help="Version of the dataset to download. "
    "If a negative integer is provided, the dataset returned is this many versions back of the latest version. "
    "Default: Latest version.",
)
def download_dataset(
    dataset_id_or_name: str, version: Optional[int],
):
    """
    Downloads a dataset from your Anyscale cloud.

    DATASET_ID_OR_NAME = ID or name of the dataset to download

    Example usage:

        anyscale llm dataset download my_dataset.jsonl

        anyscale llm dataset download file_123

    Retrieve the second latest version of the dataset:

        anyscale llm dataset download my_dataset.jsonl -v -1
    """
    anyscale.llm.dataset.download(dataset_id_or_name, version)
