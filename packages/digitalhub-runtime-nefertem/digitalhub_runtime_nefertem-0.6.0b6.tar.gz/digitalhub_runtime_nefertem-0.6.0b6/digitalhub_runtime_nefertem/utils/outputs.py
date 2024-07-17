from __future__ import annotations

import typing
from pathlib import Path

from digitalhub_core.entities._base.status import State
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.entities.artifacts.crud import create_artifact
from digitalhub_core.utils.exceptions import EntityError
from digitalhub_core.utils.logger import LOGGER
from digitalhub_runtime_nefertem.utils.env import S3_BUCKET

if typing.TYPE_CHECKING:
    from digitalhub_core.entities.artifacts.entity import Artifact


def create_artifact_(src_path: str, project: str, run_id: str) -> Artifact:
    """
    Create new artifact in backend.

    Parameters
    ----------
    src_path : str
        The artifact source local path.
    project : str
        The project name.
    run_id : str
        Neferetem run id.

    Returns
    -------
    Artifact
        DHCore artifact.
    """

    try:
        name = Path(src_path).stem.replace("_", "-")
        LOGGER.info(f"Creating new artifact '{name}'.")
        kwargs = {}
        kwargs["project"] = project
        kwargs["name"] = name
        kwargs["kind"] = "artifact"
        new_id = build_uuid()
        kwargs["uuid"] = new_id
        kwargs["path"] = f"s3://{S3_BUCKET}/{project}/artifacts/{new_id}/{Path(src_path).name}"
        artifact = create_artifact(**kwargs)
        artifact.save()
        artifact.spec.src_path = src_path
        return artifact
    except Exception as e:
        msg = f"Error creating artifact '{name}'. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise EntityError(msg) from e


def upload_artifact(artifact: Artifact) -> None:
    """
    Upload artifact to minio.

    Parameters
    ----------
    artifact : Artifact
        The artifact to upload.

    Returns
    -------
    None
    """
    try:
        LOGGER.info(f"Uploading artifact '{artifact.name}' to minio.")
        artifact.upload()
    except Exception as e:
        msg = f"Error uploading artifact '{artifact.name}'. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise EntityError(msg) from e


def build_status(results: dict, outputs: list[Artifact]) -> dict:
    """
    Build run status.

    Parameters
    ----------
    results : dict
        Neferetem run results.
    outputs : list
        The list of DHCore artifacts.

    Returns
    -------
    dict
        Run status.
    """
    try:
        return {
            "state": State.COMPLETED.value,
            "outputs": {i.name: i.key for i in outputs},
            "results": {"nefertem_result": results},
        }
    except Exception as e:
        msg = f"Something got wrong during status creation. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e
