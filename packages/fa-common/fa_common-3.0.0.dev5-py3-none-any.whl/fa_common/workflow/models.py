"""
Description: models for Workflows.

Author: Ben Motevalli (benyamin.motevalli@csiro.au)
Created: 2023-11-07
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from dateutil import parser
from pydantic import ConfigDict

from fa_common import CamelModel, get_settings
from fa_common.enums import WorkflowEnums
from fa_common.models import File
from fa_common.routes.modules.types import ModuleResponse

from .enums import ArgoWorkflowStoreType, CloudBaseImage, JobSubmitMode

######  ### ####### #          #    ######     #       #######  #####     #     #####  #     #
#     #  #     #    #         # #   #     #    #       #       #     #   # #   #     #  #   #
#        #     #    #        #   #  #     #    #       #       #        #   #  #         # #
#  ####  #     #    #       #     # ######     #       #####   #  #### #     # #          #
#     #  #     #    #       ####### #     #    #       #       #     # ####### #          #
#     #  #     #    #       #     # #     #    #       #       #     # #     # #     #    #
######  ###    #    ####### #     # ######     ####### #######  #####  #     #  #####     #


class JobRun(CamelModel):
    """JobRun"""

    id: int
    workflow_id: int
    status: str = ""
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration: Optional[float] = None
    name: str = ""
    stage: Optional[str] = None
    output: Optional[Union[List, dict]] = None
    files: Optional[List[File]] = None
    log: Optional[bytes] = None
    model_config = ConfigDict(use_enum_values=True)

    def get_compare_time(self) -> datetime:
        """get_compare_time"""
        if self.started_at is None:
            if self.status not in ["failed", "canceled", "skipped"]:
                return datetime.min.replace(tzinfo=timezone.utc)
            else:
                return datetime.now(tz=timezone.utc)
        else:
            return parser.isoparse(self.started_at)


# class WorkflowRun(CamelModel):
#     """Equivilant to  gitlab pipeline"""

#     id: int
#     gitlab_project_id: int
#     gitlab_project_branch: str
#     commit_id: str
#     status: str = ""
#     jobs: List[JobRun] = []
#     hidden_jobs: Optional[List[JobRun]] = []
#     started_at: Optional[str] = None
#     finished_at: Optional[str] = None
#     duration: Optional[int] = None


######                                                                            #
#     # ######  ####      ######  ####  #####       # #   #####   ####   ####
#     # #      #    #     #      #    # #    #     #   #  #    # #    # #    #
######  #####  #    #     #####  #    # #    #    #     # #    # #      #    #
#   #   #      #  # #     #      #    # #####     ####### #####  #  ### #    #
#    #  #      #   #      #      #    # #   #     #     # #   #  #    # #    #
#     # ######  ### #     #       ####  #    #    #     # #    #  ####   ####


class CloudStorageConfig(CamelModel):
    """
    Workflow config attributes for Cloud Storage.
    """

    access_method: WorkflowEnums.FileAccess.Method = WorkflowEnums.FileAccess.Method.DIRECT
    access_type: WorkflowEnums.FileAccess.AccessType = WorkflowEnums.FileAccess.AccessType.WITH_ROLE
    access_secret_name: Optional[str] = None
    access_secret_key: Optional[str] = None
    save_logs: bool = True

    def __init__(self, **data):
        super().__init__(**data)  # Call the superclass __init__ to handle Pydantic model initialization
        settings = get_settings()
        # Directly assign the values post-initialization if not provided
        if self.access_secret_name is None:
            self.access_secret_name = settings.STORAGE_SECRET_NAME
        if self.access_secret_key is None:
            self.access_secret_key = settings.STORAGE_SECRET_KEY

    @property
    def has_secret(self) -> bool:
        """
        checks if access type is set with secret or via a trust relationship
        through a service account.
        """
        return self.access_type == WorkflowEnums.FileAccess.AccessType.WITH_SECRET

    @property
    def cloud_base_image(self) -> str:
        """
        what cloud base image to use.
        """
        settings = get_settings()
        if settings.STORAGE_TYPE == WorkflowEnums.FileAccess.STORAGE.FIREBASE_STORAGE:
            return CloudBaseImage.GUTILS.value
        if settings.STORAGE_TYPE == WorkflowEnums.FileAccess.STORAGE.MINIO:
            return CloudBaseImage.AWS.value
        return None

    def set(self, **kwargs):
        """
        sets attributes.
        """
        for key, value in kwargs.items():
            if key == "has_secret":
                raise AttributeError("has_secret is a computed property and cannot be set directly.")
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"{self.__class__.__name__} has no attribute '{key}'")

    def set_default(self):
        """
        resets attributes to default values.
        """
        default_instance = CloudStorageConfig()
        for attr in vars(default_instance):
            setattr(self, attr, getattr(default_instance, attr))
        self.has_secret = self.access_type == WorkflowEnums.FileAccess.AccessType.WITH_SECRET


class UploadConfig(CloudStorageConfig):
    """
    Workflow config attributes for Upload Template
    """

    strategy: WorkflowEnums.Upload.Strategy = WorkflowEnums.Upload.Strategy.EVERY
    loc_name: WorkflowEnums.Upload.LocName = WorkflowEnums.Upload.LocName.POD_NAME


class RunConfig(CamelModel):
    """
    Workflow config attributes for Run Template
    """

    strategy: WorkflowEnums.Run.Strategy = WorkflowEnums.Run.Strategy.UNI_GLOBAL
    max_all_jobs_dependency: Optional[int] = 0
    save_logs: bool = True
    logging_strategy: WorkflowEnums.Logging.Strategy = WorkflowEnums.Logging.Strategy.FROM_ARTIFACT
    commands_pre: Optional[str] = "echo empty pre-command"
    commands_post: Optional[str] = "echo empty post-command"

    @property
    def is_unified(self) -> bool:
        """
        checks if access type is set with secret or via a trust relationship
        through a service account.
        """
        return "uni" in self.strategy.value


class BaseConfig(CamelModel):
    """
    Workflow config attributes for Base Template
    """

    continue_on_run_task_failure: bool = True
    is_error_tolerant: bool = False
    image_pull_secrets: List[str] = []
    service_account_name: Optional[str] = "argo-workflow-patch"
    namespace: Optional[str] = "cmr-xt-argo"
    verify_ssl: Optional[bool] = True

    @property
    def has_argo_token(self) -> bool:
        """
        checks if argo token is provided. useful for local dev.
        """
        st = get_settings()
        return not (st.ARGO_TOKEN is None or st.ARGO_TOKEN == "")

    @property
    def is_argo_local(self) -> bool:
        st = get_settings()
        return "localhost" in st.ARGO_URL


class ArgoTemplateConfig(CamelModel):
    """
    Workflow config attributes
    """

    download: CloudStorageConfig = CloudStorageConfig()
    upload: UploadConfig = UploadConfig()
    run: RunConfig = RunConfig()
    base: BaseConfig = BaseConfig()

    @property
    def logs_to_include(self) -> List:
        """
        Which logs to include.
        """
        lst_logs = []
        if self.run.save_logs:
            lst_logs.append(WorkflowEnums.Templates.RUN)
        if self.download.save_logs:
            lst_logs.append(WorkflowEnums.Templates.DOWNLOAD)
        if self.upload.save_logs:
            lst_logs.append(WorkflowEnums.Templates.UPLOAD)

        return lst_logs


class NodeResourceDuration(CamelModel):
    """
    NodeResourceDuration
    """

    cpu: Optional[int] = None
    memory: Optional[int] = None


class Parameters(CamelModel):
    """
    Parameters
    """

    name: Optional[str] = None
    value: Optional[Union[str, int]] = None


class ArgoArtifactRepoS3(CamelModel):
    """
    ArgoArtifactRepoS3
    """

    key: str


class ArgoArtifacts(CamelModel):
    """
    ArgoArtifacts
    """

    name: Optional[str] = None
    path: Optional[str] = None
    s3: Optional[ArgoArtifactRepoS3] = None


class ArgoNodeInOut(CamelModel):
    """
    ArgoNodeInOut
    """

    parameters: Optional[List[Parameters]] = None
    artifacts: Optional[List[ArgoArtifacts]] = None


class WorkflowId(CamelModel):
    """
    WorkflowId
    """

    uid: Optional[str | int] = None
    name: Optional[str] = None


class ArgoNode(CamelModel):
    """
    ArgoNode represents each node in the workflow.
    """

    id: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    type: Optional[str] = None
    template_name: Optional[str] = None
    template_scope: Optional[str] = None
    phase: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    progress: Optional[str] = None
    resources_duration: Optional[NodeResourceDuration] = None
    children: Optional[List[str]] = None
    outbound_nodes: Optional[List[str]] = None
    inputs: Optional[ArgoNodeInOut] = None
    outputs: Optional[ArgoNodeInOut] = None

    # Extra Amendments
    pod_name: Optional[str] = None
    task_name: Optional[str] = None  # This is the task name initially defined in the manifest
    output_json: Optional[Union[List, dict]] = None
    files: Optional[List[File]] = None
    log: Optional[bytes] = None
    model_config = ConfigDict(use_enum_values=True)

    def set_pod_task_names(self):
        """
        Argo Node represents each node in the workflow. Most of these nodes
        are tasks. A task is run in a kube pod, however the pod_name is not
        directly returned when getting workflow from Argo's api. This method
        will set the pod_name of each task from available fields in the
        get workflow response.
        """
        if self.id is not None and self.name is not None:
            # Set pod-name
            match = re.match(r"^(.*?)-(\d+)$", self.id if self.id is not None else "")
            if match:
                prefix, id_number = match.groups()
                self.pod_name = f"{prefix}-{self.template_name}-{id_number}"

            # Set task-name
            parts = self.name.split(".")
            self.task_name = parts[-1] if len(parts) > 1 else ""
        # @FIXME else case

    def get_compare_time(self) -> datetime:
        """
        get_compare_time
        """
        if self.started_at is None:
            if self.status not in ["Failed"]:
                return datetime.min.replace(tzinfo=timezone.utc)
            else:
                return datetime.now(tz=timezone.utc)
        else:
            return parser.isoparse(self.started_at)


class ArgoWorkflowMetadata(CamelModel):
    """
    ArgoWorkflowMetadata
    """

    name: Optional[str] = None
    generate_name: Optional[str] = None
    namespace: Optional[str] = None
    uid: Optional[str] = None
    creation_timestamp: Optional[str] = None


class ArgoWorkflowStatus(CamelModel):
    """
    ArgoWorkflowStatus
    """

    phase: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    progress: Optional[str] = None
    nodes: Optional[List[ArgoNode]] = []


T = TypeVar("T", bound="ArgoWorkflowRun")


class ArgoWorkflowRun(CamelModel):
    """
    ArgoWorkflowRun
    """

    metadata: Optional[ArgoWorkflowMetadata] = None
    status: Optional[ArgoWorkflowStatus] = None
    spec: Optional[dict] = {}
    jobs: Optional[List[JobRun]] = []

    @classmethod
    def populate_from_res(cls: Type[T], res, fields) -> T:
        """
        This method populates ArgoWorkflowRun attributes
        from the response received from getting the
        workflow
        """
        try:
            res_dict = res if isinstance(res, dict) else res.to_dict()

            init_args: Dict[str, Any] = {}
            if "metadata" in fields:
                init_args["metadata"] = ArgoWorkflowMetadata(**res_dict.get("metadata", {}))
            if "status" in fields:
                status = res_dict.get("status", {})
                if ("nodes" in status) and (isinstance(status["nodes"], dict)):
                    nodes = []
                    for _, v in status["nodes"].items():
                        nodes.append(v)
                    status["nodes"] = nodes
                init_args["status"] = ArgoWorkflowStatus(**status)
            if "spec" in fields:
                init_args["spec"] = res_dict.get("spec", {})

            return cls(**init_args)
        except Exception as e:
            raise ValueError("Could not parse response") from e


######  #######  #####           # ####### ######     ######
#     # #       #     #          # #     # #     #    #     # ###### ###### # #    # # ##### #  ####  #    #  ####
#     # #       #     #          # #     # #     #    #     # #      #      # ##   # #   #   # #    # ##   # #
######  #####   #     #          # #     # ######     #     # #####  #####  # # #  # #   #   # #    # # #  #  ####
#   #   #       #   # #    #     # #     # #     #    #     # #      #      # #  # # #   #   # #    # #  # #      #
#    #  #       #    #     #     # #     # #     #    #     # #      #      # #   ## #   #   # #    # #   ## #    #
#     # #######  #### #     #####  ####### ######     ######  ###### #      # #    # #   #   #  ####  #    #  ####


class GetWorkflowRes(CamelModel):
    """
    GetWorkflowRes
    """

    workflow: Any = None
    is_found: bool = False
    source_type: Optional[ArgoWorkflowStoreType] = None


class InputJobTemplate(CamelModel):
    """
    InputJobTemplate
    """

    files: Optional[List[File]] = []
    parameters: str | dict = '"{"message": "no inputs!"}"'


class JobSecrets(CamelModel):
    """
    :param: name: name of secret
    :param: mount_path: where to mount the secret.
    """

    name: Optional[str] = None
    mount_path: Optional[str] = None


class WorkflowCallBack(CamelModel):
    """
    This class defines callback attributes. Callback executes
    in the Archive Node as this node runs onExit event hook.
    Callback can be used to notify client that a workflow is completed
    and it can be used to handle post-workflow logics.

    Note that callback should be implemented in the backend
    api. The callback api then is called in the workflow.

    :param: url: callback url (implemented in the backend api)
    :param: metadata: A json string used to input metadata that you want to
    receive back on the callback, e.g. project_name.
    :param: env_secrets: can be used to pass required secrets for the
    callback, e.g. API key.
    :param: env_vars: can be used to pass required secrets for the
    callback, e.g. API key. With env_vars, the secrets can directly
    be passed from the backend api.
    """

    url: str  # URL for callback
    metadata: Optional[str] = ""
    env_secrets: List[str] = []
    env_vars: Dict = {}


class JobUploads(CamelModel):
    """
    :param: `default_path`: this is the default path constructed from
    WORKFLOW_UPLOAD_PATH. All logs and workflow steps are stored here.
    Also, this is the default path where outputs of a job are stored.

    :param: `custom_path`: if defined, the main outputs of the job
    is stored in this location, instead of the default location.

    :param: `copy_paths`: this is used, if a copy of the main outputs
    are required in other locations as well.

    :param: `selected_outputs`: if empty, copies all outputs. Note
    the paths in selected_outputs are subpaths of the outputs folder
    within the container (defined by output_path in JobTemplate). These
    paths can point to either file or folder.
    """

    default_path: str = ""
    custom_path: Optional[str] = None
    copy_paths: Optional[List[str]] = []
    selected_outputs: Optional[List[str]] = []

    @property
    def is_custom_upload(self):
        return self.custom_path is not None and self.custom_path != ""

    @property
    def has_all_outputs(self):
        return len(self.selected_outputs) == 0


class JobResource(CamelModel):
    cpu_req: str | float
    mem_req: str
    cpu_limit: str | float
    mem_limit: str


class LocalTemplateConfig(CamelModel):
    standalone_base_path: str


class JobTemplate(CamelModel):
    """
    JobTemplate is definition of individual job (and not necessarily a task).
    """

    custom_id: Union[int, str] = None
    name: Optional[str] = None
    module: ModuleResponse
    submit_mode: JobSubmitMode
    inputs: Optional[Union[InputJobTemplate, List[InputJobTemplate]]] = None
    dependency: Optional[List[str]] = []
    uploads: Optional[JobUploads] = None
    template_config: Optional[ArgoTemplateConfig | LocalTemplateConfig] = None
    resources: Optional[JobResource] = None
    env_vars: Dict = {}
    callbacks: Optional[List[WorkflowCallBack]] = []
