from __future__ import annotations

import typing

from digitalhub_core.entities._builders.metadata import build_metadata
from digitalhub_core.entities._builders.name import build_name
from digitalhub_core.entities._builders.spec import build_spec
from digitalhub_core.entities._builders.status import build_status
from digitalhub_data.entities.projects.entity import CTX_ENTITIES, FUNC_MAP, ProjectData
from digitalhub_ml.entities.entity_types import EntityTypes
from digitalhub_ml.entities.models.crud import (
    create_model_from_dict,
    delete_model,
    get_model,
    list_models,
    log_model,
    new_model,
)

if typing.TYPE_CHECKING:
    from digitalhub_ml.entities.models.entity import Model

MODELS = EntityTypes.MODELS.value
CTX_ENTITIES.append(MODELS)
FUNC_MAP[MODELS] = create_model_from_dict


class ProjectMl(ProjectData):
    """
    ProjectMl class.
    """

    #############################
    #  Models
    #############################

    def new_model(
        self,
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
        obj = new_model(
            project=self.name,
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
        self.refresh()
        return obj

    def get_model(
        self,
        identifier: str,
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
            Instance of Model class.
        """
        obj = get_model(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            **kwargs,
        )
        self.refresh()
        return obj

    def delete_model(
        self,
        identifier: str,
        entity_id: str | None = None,
        delete_all_versions: bool = False,
        **kwargs,
    ) -> None:
        """
        Delete a Model from project.

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
        None
        """
        delete_model(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            delete_all_versions=delete_all_versions,
            **kwargs,
        )
        self.refresh()

    def list_models(self, **kwargs) -> list[dict]:
        """
        List models associated with the project.

        Parameters
        ----------
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        list[dict]
            List of objects related to project.
        """
        return list_models(self.name, **kwargs)

    def log_model(
        self,
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
        obj = log_model(
            project=self.name,
            name=name,
            kind=kind,
            path=path,
            source_path=source_path,
            **kwargs,
        )
        self.refresh()
        return obj

    @staticmethod
    def _parse_dict(obj: dict, validate: bool = True) -> dict:
        """
        Get dictionary and parse it to a valid entity dictionary.

        Parameters
        ----------
        entity : str
            Entity type.
        obj : dict
            Dictionary to parse.

        Returns
        -------
        dict
            A dictionary containing the attributes of the entity instance.
        """
        # Override methods to search in digitalhub_ml
        name = build_name(obj.get("name"))
        kind = obj.get("kind")
        metadata = build_metadata(kind, **obj.get("metadata", {}))
        spec = build_spec(kind, validate=validate, **obj.get("spec", {}))
        status = build_status(kind, **obj.get("status", {}))
        user = obj.get("user")
        local = obj.get("local", False)
        return {
            "name": name,
            "kind": kind,
            "metadata": metadata,
            "spec": spec,
            "status": status,
            "user": user,
            "local": local,
        }


def project_from_parameters(
    name: str,
    kind: str,
    description: str | None = None,
    git_source: str | None = None,
    labels: list[str] | None = None,
    local: bool = False,
    context: str | None = None,
    **kwargs,
) -> ProjectData:
    """
    Create project.

    Parameters
    ----------
    name : str
        Object name.
    kind : str
        Kind the object.
    description : str
        Description of the object (human readable).
    git_source : str
        Remote git source for object.
    labels : list[str]
        List of labels.
    local : bool
        Flag to determine if object will be exported to backend.
    context : str
        The context of the project.
    **kwargs : dict
        Spec keyword arguments.

    Returns
    -------
    ProjectData
        ProjectData object.
    """
    name = build_name(name)
    spec = build_spec(
        kind,
        context=context,
        **kwargs,
    )
    metadata = build_metadata(
        kind,
        project=name,
        name=name,
        description=description,
        labels=labels,
        source=git_source,
    )
    status = build_status(kind)
    return ProjectMl(
        name=name,
        kind=kind,
        metadata=metadata,
        spec=spec,
        status=status,
        local=local,
    )


def project_from_dict(obj: dict) -> ProjectData:
    """
    Create project from dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    ProjectData
        ProjectData object.
    """
    return ProjectMl.from_dict(obj)
