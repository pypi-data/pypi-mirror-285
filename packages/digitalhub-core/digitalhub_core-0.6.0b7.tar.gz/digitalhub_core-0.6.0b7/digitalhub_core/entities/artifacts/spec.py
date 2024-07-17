from __future__ import annotations

from digitalhub_core.entities._base.spec import Spec, SpecParams


class ArtifactSpec(Spec):
    """
    Artifact specification.
    """

    def __init__(
        self,
        path: str | None = None,
        src_path: str | None = None,
        **kwargs,
    ) -> None:
        self.path = path
        self.src_path = src_path


class ArtifactParams(SpecParams):
    """
    Artifact base parameters.
    """

    path: str = None
    """Target path of the artifact."""

    src_path: str = None
    """Source path of the artifact."""


class ArtifactSpecArtifact(ArtifactSpec):
    """
    Artifact specification.
    """


class ArtifactParamsArtifact(ArtifactParams):
    """
    Artifact parameters.
    """
