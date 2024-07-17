from __future__ import annotations

import typing

from digitalhub_core.utils.exceptions import EntityError
from digitalhub_core.utils.logger import LOGGER

if typing.TYPE_CHECKING:
    from digitalhub_data.entities.dataitems.entity._base import Dataitem


def persist_dataitem(dataitem: Dataitem, name: str, output_path: str) -> dict:
    """
    Persist dataitem locally.

    Parameters
    ----------
    dataitem : Dataitem
        The dataitem to persist.
    name : str
        The dataitem name.
    output_path : str
        The dataitem output path.

    Returns
    -------
    dict
        The dataitem path.

    Raises
    ------
    EntityError
        If the dataitem cannot be persisted.
    """
    try:
        LOGGER.info(f"Persisting dataitem '{name}' locally.")
        tmp_path = f"{output_path}/tmp/{name}.csv"
        dataitem.as_df().to_csv(tmp_path, sep=",", index=False)
        return {"name": name, "path": tmp_path}
    except Exception as e:
        msg = f"Error during dataitem '{name}' collection. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise EntityError(msg) from e
