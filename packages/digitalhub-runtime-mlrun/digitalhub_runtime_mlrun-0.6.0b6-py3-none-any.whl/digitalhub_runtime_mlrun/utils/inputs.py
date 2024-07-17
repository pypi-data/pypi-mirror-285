from __future__ import annotations

import typing
from pathlib import Path

from digitalhub_core.entities.artifacts.crud import artifact_from_dict
from digitalhub_core.entities.utils import parse_entity_key
from digitalhub_core.utils.exceptions import EntityError
from digitalhub_core.utils.logger import LOGGER
from digitalhub_data.entities.dataitems.crud import dataitem_from_dict
from digitalhub_data.readers.builder import get_reader_by_object
from digitalhub_ml.entities.models.crud import model_from_dict

if typing.TYPE_CHECKING:
    from digitalhub_core.entities._base.entity import Entity
    from digitalhub_core.entities.artifacts.entity import Artifact
    from digitalhub_data.entities.dataitems.entity.table import DataitemTable
    from digitalhub_ml.entities.models.entity import Model


def persist_dataitem(dataitem: DataitemTable, tmp_dir: Path) -> str:
    """
    Persist dataitem locally.

    Parameters
    ----------
    dataitem : DataitemTable
        The dataitem to persist.
    tmp_dir : Path
        Temporary download directory.

    Returns
    -------
    str
        Temporary dataitem path.

    Raises
    ------
    EntityError
        If the dataitem cannot be persisted.
    """
    name = dataitem.name
    try:
        LOGGER.info(f"Persisting dataitem '{name}' locally.")
        tmp_path = str(tmp_dir / f"{name}.csv")
        df = dataitem.as_df()
        get_reader_by_object(df).write_csv(df, tmp_path)
        return tmp_path
    except Exception as e:
        msg = f"Error during dataitem '{name}' collection. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise EntityError(msg) from e


def persist_artifact(artifact: Artifact, tmp_dir: Path) -> str:
    """
    Persist artifact locally.

    Parameters
    ----------
    artifact : Artifact
        The artifact object.
    tmp_dir : Path
        Temporary directory.

    Returns
    -------
    str
        Temporary artifact path.

    Raises
    ------
    EntityError
        If the artifact cannot be persisted.
    """
    name = artifact.name
    try:
        LOGGER.info(f"Persisting artifact '{name}' locally.")
        filename = Path(artifact.spec.path).name
        dst = str(tmp_dir / filename)
        return artifact.download(dst=dst)
    except Exception as e:
        msg = f"Error during artifact '{name}' collection. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise EntityError(msg) from e


def persist_model(model: Model, tmp_dir: Path) -> str:
    """
    Persist model locally.

    Parameters
    ----------
    model : Model
        The model object.
    tmp_dir : Path
        Temporary directory.

    Returns
    -------
    str
        Temporary model path.

    Raises
    ------
    EntityError
        If the model cannot be persisted.
    """
    name = model.name
    try:
        LOGGER.info(f"Persisting model '{name}' locally.")
        filename = Path(model.spec.path).name
        dst = str(tmp_dir / filename)
        return model.download(dst=dst)
    except Exception as e:
        msg = f"Error during model '{name}' collection. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise EntityError(msg) from e


def get_inputs_parameters(inputs: dict[str, Entity], parameters: dict, tmp_dir: Path) -> dict:
    """
    Set inputs.

    Parameters
    ----------
    inputs : dict[str, Entity]
        Run inputs.
    parameters : dict
        Run parameters.
    tmp_dir : Path
        Temporary directory for storing dataitms and artifacts.

    Returns
    -------
    dict
        Mlrun inputs.
    """
    inputs_objects = {}
    for k, v in inputs.items():
        _, entity_type, _, _, _ = parse_entity_key(v.get("key"))
        if entity_type == "dataitems":
            v = dataitem_from_dict(v)
            inputs_objects[k] = persist_dataitem(v, tmp_dir)
        elif entity_type == "artifacts":
            v = artifact_from_dict(v)
            inputs_objects[k] = persist_artifact(v, tmp_dir)
        elif entity_type == "models":
            v = model_from_dict(v)
            inputs_objects[k] = persist_model(v, tmp_dir)
    return {"inputs": inputs_objects | parameters.pop("inputs", {}), "params": parameters}
