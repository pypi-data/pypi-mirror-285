"""
Description: Enumerators for Workflows.

Author: Ben Motevalli (benyamin.motevalli@csiro.au)
Created: 2023-11-07
"""

from enum import Enum


class CloudBaseImage(str, Enum):
    """
    CloudBaseImage for download and upload
    """

    AWS = "benmotevalli/aws-jq-curl"
    GUTILS = "benmotevalli/gsutil-jq-curl"


# class ModuleType(str, Enum):
#     """
#     ModuleType
#     """

#     SYNC = "sync"  # Is run via a service call
#     ASYNC = "async"  # Is executed via gitlab ci


class JobAction(str, Enum):
    """
    JobAction
    """

    PLAY = "play"
    RETRY = "retry"
    DELETE = "delete"
    CANCEL = "cancel"


class JobSecretTypes(str, Enum):
    """
    JobSecretTypes
    """

    ENV = "ENV"
    MOUNT = "MOUNT"


class JobStatus(str, Enum):
    """
    JobStatus
    """

    NOT_SET = ""
    RECEIVED = "RECEIVED"
    PENDING = "PENDING"  # argo, gitlab
    RUNNING = "RUNNING"  # argo, gitlab
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"  # argo, gitlab
    SUCCEEDED = "SUCCEEDED"  # argo


class JobSubmitMode(str, Enum):
    """
    JobSubmitMode

    ISOLATED:       runs in isolated container via Argo. The image used should be self-contained
    LOCAL:          runs on the backend api
    ISOLATED_LOCAL: runs in isolated container via Argo, but it downloads the module repo into a
                    common base image.
    """

    ISOLATED = "isolated"
    LOCAL = "local"
    ISOLATED_LOCAL = "isolated-local"


class ArgoWorkflowStoreType(str, Enum):
    """
    ArgoWorkflowStoreType
    """

    LIVE = "live"
    STORAGE = "storage"
    ARCHIVE = "archive"
