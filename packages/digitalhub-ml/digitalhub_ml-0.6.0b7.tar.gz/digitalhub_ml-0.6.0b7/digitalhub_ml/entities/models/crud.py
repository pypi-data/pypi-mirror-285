from __future__ import annotations

import typing

from digitalhub_core.context.builder import check_context
from digitalhub_core.entities._base.crud import (
    delete_entity_api_ctx,
    list_entity_api_ctx,
    read_entity_api_ctx,
    update_entity_api_ctx,
)
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.utils.env_utils import get_s3_bucket
from digitalhub_core.utils.file_utils import get_file_name
from digitalhub_core.utils.io_utils import read_yaml
from digitalhub_ml.entities.entity_types import EntityTypes
from digitalhub_ml.entities.models.entity import model_from_dict, model_from_parameters

if typing.TYPE_CHECKING:
    from digitalhub_ml.entities.models.entity import Model


ENTITY_TYPE = EntityTypes.MODELS.value


def create_model(**kwargs) -> Model:
    """
    Create a new Model instance with the specified parameters.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments.

    Returns
    -------
    Model
        An instance of the created model.
    """
    return model_from_parameters(**kwargs)


def create_model_from_dict(obj: dict) -> Model:
    """
    Create a new Model instance from a dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    Model
        Model object.
    """
    check_context(obj.get("project"))
    return model_from_dict(obj)


def new_model(
    project: str,
    name: str,
    kind: str,
    uuid: str | None = None,
    description: str | None = None,
    git_source: str | None = None,
    labels: list[str] | None = None,
    embedded: bool = True,
    path: str | None = None,
    framework: str | None = None,
    algorithm: str | None = None,
    **kwargs,
) -> Model:
    """
    Create a new Model instance with the specified parameters.

    Parameters
    ----------
    project : str
        Project name.
    name : str
        Object name.
    kind : str
        Kind the object.
    uuid : str
        ID of the object (UUID4).
    description : str
        Description of the object (human readable).
    git_source : str
        Remote git source for object.
    labels : list[str]
        List of labels.
    embedded : bool
        Flag to determine if object must be embedded in project.
    path : str
        Object path on local file system or remote storage.
        If not provided, it's generated.
    framework : str
        Model framework (e.g. 'pytorch').
    algorithm : str
        Model algorithm (e.g. 'resnet').
    **kwargs : dict
        Spec keyword arguments.

    Returns
    -------
    Model
        An instance of the created model.
    """
    obj = create_model(
        project=project,
        name=name,
        kind=kind,
        uuid=uuid,
        description=description,
        git_source=git_source,
        labels=labels,
        embedded=embedded,
        path=path,
        framework=framework,
        algorithm=algorithm,
        **kwargs,
    )
    obj.save()
    return obj


def get_model(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    **kwargs,
) -> Model:
    """
    Get object from backend.

    Parameters
    ----------
    identifier : str
        Entity key or name.
    project : str
        Project name.
    entity_id : str
        Entity ID.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    Model
        Object instance.
    """

    obj = read_entity_api_ctx(
        identifier,
        ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        **kwargs,
    )
    return model_from_dict(obj)


def import_model(file: str) -> Model:
    """
    Import an Model object from a file using the specified file path.

    Parameters
    ----------
    file : str
        Path to the file.

    Returns
    -------
    Model
        Object instance.
    """
    obj: dict = read_yaml(file)
    return create_model_from_dict(obj)


def delete_model(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    delete_all_versions: bool = False,
    **kwargs,
) -> dict:
    """
    Delete object from backend.

    Parameters
    ----------
    identifier : str
        Entity key or name.
    project : str
        Project name.
    entity_id : str
        Entity ID.
    delete_all_versions : bool
        Delete all versions of the named entity.
        Use entity name instead of entity key as identifier.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.
    """
    return delete_entity_api_ctx(
        identifier=identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        delete_all_versions=delete_all_versions,
        **kwargs,
    )


def update_model(entity: Model, **kwargs) -> Model:
    """
    Update object in backend.

    Parameters
    ----------
    entity : Model
        The object to update.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    Model
        Entity updated.
    """
    obj = update_entity_api_ctx(
        project=entity.project,
        entity_type=ENTITY_TYPE,
        entity_id=entity.id,
        entity_dict=entity.to_dict(),
        **kwargs,
    )
    return model_from_dict(obj)


def list_models(project: str, **kwargs) -> list[Model]:
    """
    List all objects from backend.

    Parameters
    ----------
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[Model]
        List of models.
    """
    objs = list_entity_api_ctx(
        project=project,
        entity_type=ENTITY_TYPE,
        **kwargs,
    )
    return [model_from_dict(obj) for obj in objs]


def log_model(
    project: str,
    name: str,
    kind: str,
    path: str | None = None,
    source_path: str | None = None,
    **kwargs,
) -> Model:
    """
    Create and upload an model.

    Parameters
    ----------
    project : str
        Project name.
    name : str
        Object name.
    kind : str
        Kind the object.
    path : str
        Destination path of the model.
    source_path : str
        Model location on local machine.
    **kwargs : dict
        New model parameters.

    Returns
    -------
    Model
        Instance of Model class.
    """
    if path is None:
        if source_path is None:
            raise Exception("Either path or source_path must be provided.")

        # Build path if not provided from source filename
        filename = get_file_name(source_path)
        uuid = build_uuid()
        kwargs["uuid"] = uuid
        path = f"s3://{get_s3_bucket()}/{project}/{ENTITY_TYPE}/{name}/{uuid}/{filename}"

    obj = new_model(project=project, name=name, kind=kind, path=path, **kwargs)
    obj.upload(source_path)
    return obj
