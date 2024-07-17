from __future__ import annotations

from digitalhub_data.entities.projects.spec import ProjectParamsData, ProjectSpecData


class ProjectSpecMl(ProjectSpecData):
    """
    Project specification.
    """

    def __init__(
        self,
        context: str | None = None,
        functions: list | None = None,
        artifacts: list | None = None,
        workflows: list | None = None,
        dataitems: list | None = None,
        models: list | None = None,
        **kwargs,
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        models : list
            List of project's models.
        """
        super().__init__(context, functions, artifacts, workflows, dataitems, **kwargs)
        self.models = models if models is not None else []


class ProjectParamsMl(ProjectParamsData):
    """
    Parameters model for project.
    """

    models: list = None
    """List of project's models."""
