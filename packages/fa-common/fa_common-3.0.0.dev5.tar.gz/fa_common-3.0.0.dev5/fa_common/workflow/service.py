"""
@REVIEW:
- Below service functions works for both Argo and Gitlab.
- They are moved from gitlab_service
"""

import json
from typing import List, Union

from fa_common import File, get_settings
from fa_common.enums import WorkflowEnums
from fa_common.models import BucketMeta
from fa_common.storage import get_storage_client

from .models import ArgoNode, JobRun


class WorkflowService:
    @classmethod
    async def get_job_output(cls, bucket_id: BucketMeta, workflow_id: Union[int, str], job_id: Union[int, str]) -> Union[dict, List, None]:
        # client = get_workflow_client()
        storage = get_storage_client()
        file_path = f"{bucket_id.base_path}/{workflow_id}/{job_id}/outputs.json"
        # storage.add_project_base_path(bucket_id, f"{st.WORKFLOW_UPLOAD_PATH}/{workflow_id}/{job_id}/outputs.json")
        file = await storage.get_file(
            bucket_id.name,
            file_path,
        )
        if file is None:
            return None
        return json.load(file)

    @classmethod
    async def get_job_file_refs(cls, bucket_id: BucketMeta, workflow_id: Union[str, int], job_id: Union[str, int]) -> List[File]:
        storage = get_storage_client()
        folder_path = f"{bucket_id.base_path}/{workflow_id}/{job_id}/"

        # storage.add_project_base_path(bucket_id, f"{st.WORKFLOW_UPLOAD_PATH}/{workflow_id}/{job_id}/")
        return await storage.list_files(
            bucket_id.name,
            folder_path,
        )

    @classmethod
    async def add_data_to_job(cls, job: JobRun, bucket_id: BucketMeta, output: bool = True, file_refs: bool = True) -> JobRun:
        if job.status == "success":
            if file_refs:
                job.files = await cls.get_job_file_refs(bucket_id, job.workflow_id, job.id)
            if output and job.output is None:
                job.output = await cls.get_job_output(bucket_id, job.workflow_id, job.id)
        return job

    @classmethod
    async def add_data_to_argo_node(
        cls,
        node: ArgoNode,
        bucket_id: BucketMeta,
        workflow_uname: str,
        config_upload_loc: WorkflowEnums.Upload.LocName,
        output: bool = True,
        file_refs: bool = True,
    ) -> JobRun:
        if node.phase == "Succeeded" and node.template_name == WorkflowEnums.Templates.RUN:
            node.set_pod_task_names()
            subfolder = node.pod_name if config_upload_loc == WorkflowEnums.Upload.LocName.POD_NAME else node.task_name

            if file_refs:
                node.files = await cls.get_job_file_refs(bucket_id, workflow_uname, subfolder)
            if output and node.output_json is None:
                node.output_json = await cls.get_job_output(bucket_id, workflow_uname, subfolder)
        return node

    @classmethod
    def get_workflow_bucket_from_settings(cls, bucket_id: str):
        """
        If workflow apis are used in a project, use this to get back the BucketMeta object from
        project settings.
        """
        storage = get_storage_client()
        st = get_settings()
        return BucketMeta(name=st.BUCKET_NAME, base_path=storage.get_standard_workflow_upload_path(bucket_id))

    # @classmethod
    # async def get_job_run(
    #     cls,
    #     user_id: str,
    #     bucket_id: BucketMeta,
    #     job_id: int,
    #     include_log: bool = False,
    #     output: bool = True,
    #     file_refs: bool = True,
    # ) -> JobRun:
    #     client = get_workflow_client()
    #     job = await client.get_job(user_id, job_id, include_log, output)
    #     job = await cls.add_data_to_job(job, bucket_id, output, file_refs)
    #     return job
