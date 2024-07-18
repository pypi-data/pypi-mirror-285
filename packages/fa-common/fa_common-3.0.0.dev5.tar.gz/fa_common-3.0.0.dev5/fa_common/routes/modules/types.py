from copy import deepcopy
from typing import Any, List, Optional, Union

from fa_common.enums import WorkflowEnums
from fa_common.models import BucketMeta, CamelModel

from .enums import ModuleRunModes, ModuleType, ModuleUsability, ModuleVisibility, ParamType


def deep_merge(base: Any, overlay: Any) -> Any:
    """
    Recursively merge properties of two complex objects.

    Args:
        base (Any): The base object, which provides default values.
        overlay (Any): The overlay object, whose values take precedence.

    Returns:
        Any: The result of deeply merged objects.
    """
    if isinstance(base, CamelModel) and isinstance(overlay, CamelModel):
        # Ensure both objects are instances of CamelModel before merging
        for field in base.model_fields:
            base_value = getattr(base, field)
            overlay_value = getattr(overlay, field, None)
            if overlay_value is not None:
                # Recursive merge if both are CamelModels, else overlay takes precedence
                if isinstance(base_value, CamelModel) and isinstance(overlay_value, CamelModel):
                    setattr(base, field, deep_merge(base_value, overlay_value))
                else:
                    setattr(base, field, overlay_value)
        return base
    elif isinstance(base, list) and isinstance(overlay, list):
        # Extend or replace lists
        return overlay  # This can be customized if you need to merge lists differently
    return overlay if overlay is not None else base


class Parameter(CamelModel):
    name: str
    type: ParamType
    unit_in: Optional[str] = None
    unit_std: Optional[str] = None
    unit_display: Optional[str] = None
    display_name: Optional[str] = None


class RunModule(CamelModel):
    cmd: Optional[Union[str, List[str]]] = None
    mode: ModuleRunModes
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    parameters: Optional[List[Parameter]] = None


class JobSecrets(CamelModel):
    name: str
    mount_path: str


class ModuleImage(CamelModel):
    url: str
    run_meta: Optional[RunModule] = None
    image_pull_secrets: Optional[List[str]] = []
    image_pull_policy: Optional[WorkflowEnums.Run.ImagePullPolicy] = WorkflowEnums.Run.ImagePullPolicy.IF_NOT_PRESENT
    env_secrets: Optional[List[str]] = []
    mount_secrets: Optional[List[JobSecrets]] = []
    env_configs: Optional[List[str]] = []


class ModuleRepository(CamelModel):
    bucket: BucketMeta
    run_meta: Optional[RunModule] = None
    use_tmp_dir: bool
    base_image: Optional[str] = None
    ignore_copy: Optional[List[str]] = None


class ModuleMeta(CamelModel):
    """
    Contains Module's metadata.

    A single version could include both a repo_ref and an image_ref.
    Note an image_ref can only be run through argo (or a remote workflow runner).
    While, repo_ref can be run both locally or through a base image that downloads the
    repo ref and runs it in a remote workflow runner (eg. argo).
    """

    visibility: Optional[ModuleVisibility] = None
    usability: Optional[List[ModuleUsability]] = []
    type: Optional[Union[ModuleType, List[ModuleType]]] = None
    image_ref: Optional[ModuleImage] = None
    repo_ref: Optional[ModuleRepository] = None


class ModuleVersion(CamelModel):
    name: str
    labels: Optional[List[str]] = []
    module_meta: Optional[ModuleMeta] = None


class Module(CamelModel):
    name: str
    versions: List[ModuleVersion]
    base_version: Optional[ModuleVersion]
    # module_meta: Optional[ModuleMeta] = None

    def get_fused_version_meta(self, version_name: str) -> ModuleVersion:
        """
        Retrieves a version by its label and fuses its properties with module-level metadata.

        Parameters:
            version_label (str): The label of the version to retrieve.

        Returns:
            Optional[ModuleVersion]: A new ModuleVersion instance with fused properties,
                                     or None if the version is not found.
        """
        # Find the specified version
        version = next((v for v in self.versions if v.name == version_name), None)
        if not version:
            raise ValueError(f"Version {version_name} was not found!")

        # # Create a new ModuleVersion instance to avoid mutating the original
        # fused_version = ModuleVersion(name=version.name, label=version.labels)

        # Merge version and base_version
        if self.base_version:
            return deep_merge(deepcopy(self.base_version), deepcopy(version))

        return version


class ModuleResponse(CamelModel):
    name: str
    version: ModuleVersion
