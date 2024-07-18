from typing import Optional

from anyscale._private.sdk.base_sdk import BaseSDK


def upload(
    dataset_file: str,
    existing_dataset_id_or_name: Optional[str] = None,
    *,
    description: Optional[str] = None,
    cloud_id: Optional[str] = None,
    project_id: Optional[str] = None,
):
    """Uploads a dataset, or a new version of a dataset, to your Anyscale cloud.

    :param dataset_file: Path to the dataset file to upload.
    :param existing_dataset_id_or_name: ID or name of an existing dataset to upload a new version of. If not provided, a new dataset will be created.
    :param description: Description of the dataset (or dataset version).
    :param cloud_id: ID of the Anyscale cloud to upload a new dataset to. If not provided, the default Anyscale Hosted cloud will be used.
    :param project_id: ID of the Anyscale project to upload a new dataset to. If not provided, the default project of the cloud will be used.

    Example usage:
    ```python
    anyscale.llm.dataset.upload("path/to/my_dataset.jsonl")
    anyscale.llm.dataset.upload("my_dataset2.jsonl", "file_123")
    anyscale.llm.dataset.upload("my_dataset2.jsonl", "my_dataset.jsonl", description="added 3 lines")
    ```
    :return: The `Dataset` object representing the uploaded dataset.

    NOTE:
    If you are uploading a new version, have run this from within an Anyscale workspace,
    and neither `cloud_id` nor `project_id` are provided, the cloud and project of the workspace will be used.
    """
    _sdk = BaseSDK()
    _sdk.client.upload_dataset(
        dataset_file, existing_dataset_id_or_name, description, cloud_id, project_id,
    )


def download(
    dataset_id_or_name: str, version: Optional[int] = None  # noqa: ARG001
) -> bytes:
    """Downloads a dataset from your Anyscale cloud.

    :param dataset_id_or_name: ID or name of the dataset to download.
    :param version: Version of the dataset to download. If a negative integer is provided, the dataset returned is this many versions back of the latest version. Default: Latest version.

    Example usage:
    ```python
    dataset_contents = anyscale.llm.dataset.download("my_dataset.jsonl") # anyscale.llm.dataset.download("file_123")
    jsonl_obj = [json.loads(line) for line in dataset_contents.decode().splitlines()]

    prev_dataset_contents = anyscale.llm.dataset.download("my_dataset.jsonl", version=-1)
    ```
    :return: The contents of the dataset file.
    """
    _sdk = BaseSDK()
    dataset_bytes = _sdk.client.download_dataset(dataset_id_or_name, version)
    return dataset_bytes
