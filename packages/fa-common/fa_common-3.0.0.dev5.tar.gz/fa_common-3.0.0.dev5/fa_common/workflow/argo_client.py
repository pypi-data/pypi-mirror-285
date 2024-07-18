"""
The `ArgoClient` class is a singleton client in Python for interacting with Argo workflows,
providing specialized functions for job/module workflows and handling workflow submissions, runs,
retrievals, logs, and deletions.
"""

import json
from copy import deepcopy
from typing import Dict, List, Optional, Union

import httpx
from argo_workflows import ApiClient
from argo_workflows.api import workflow_service_api
from argo_workflows.exceptions import (
    ApiException,
    ForbiddenException,
    NotFoundException,
)

from fa_common import get_current_app
from fa_common import logger as LOG
from fa_common.exceptions import BadRequestError, NotFoundError
from fa_common.models import BucketMeta
from fa_common.storage import get_storage_client

from .argo_utils import ArgoTemplateGenerator
from .base_client import WorkflowBaseClient
from .enums import ArgoWorkflowStoreType, JobStatus
from .models import (
    ArgoWorkflowRun,
    GetWorkflowRes,
    JobTemplate,
    WorkflowId,
)
from .service import WorkflowService


class ArgoClient(WorkflowBaseClient):
    """
    Singleton client for interacting with argo-workflows.
    Is a wrapper over the existing argo-workflows python client to provide specialist functions for
    the Job/Module workflow.

    Please don't use it directly, use `fa_common.workflow.utils.get_workflow_client`.
    """

    __instance = None
    argo_workflow_client: ApiClient
    workflow_service: workflow_service_api.WorkflowServiceApi
    template_generator: ArgoTemplateGenerator
    api_headers: dict
    api_url: str

    def __new__(cls) -> "ArgoClient":
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            app = get_current_app()
            cls.__instance.argo_workflow_client = app.argo_workflow_client  # type: ignore
            cls.__instance.workflow_service = workflow_service_api.WorkflowServiceApi(cls.__instance.argo_workflow_client)
            cls.__instance.template_generator = ArgoTemplateGenerator()
            cls.__instance.api_headers = cls.__instance.argo_workflow_client.default_headers
            cls.__instance.api_url = f"{cls.__instance.argo_workflow_client.configuration.host}/api/v1"
        return cls.__instance

    ######
    #     # #    # #    #
    #     # #    # ##   #
    ######  #    # # #  #
    #   #   #    # #  # #
    #    #  #    # #   ##
    #     #  ####  #    #

    # @retry(times=1, delay=5)

    def _get_job_config(self, job: JobTemplate):
        return job.template_config if job.template_config is not None else self.template_generator.config

    async def submit(self, argo_workflow, namespace: str, verify_ssl=True) -> ArgoWorkflowRun:
        """
        This Python async function submits an Argo workflow and handles any ApiException
        that may occur.

        :param argo_workflow: `argo_workflow` is an object representing an Argo workflow
        that will be submitted for execution. It contains the necessary information and
        specifications for the workflow to be executed by the Argo workflow service

        :return: The `submit` method returns an `ArgoWorkflowRun` object that is populated
        with specific fields from the API response. The `ArgoWorkflowRun` object is created
        by calling the `populate_from_res` method with the API response and specifying the
        fields to include in the object.
        """
        try:
            res = await self.api_post(
                route=f"workflows/{namespace}",
                body={"workflow": argo_workflow},
                verify_ssl=verify_ssl,
            )
            # api_response = await force_async(self.workflow_service.create_workflow)(
            #     namespace="cmr-xt-argo",
            #     body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(
            #         workflow=argo_workflow, _check_type=False
            #     ),
            #     _check_return_type=False,
            # )

            if res.status_code == 400:
                raise BadRequestError(res.read())

            return ArgoWorkflowRun.populate_from_res(res.json(), fields=["metadata", "status"])  # self.format_workflow_resp(api_response)

        except ApiException as err:
            LOG.warning(f"Workflow submission Error caught: {err}")  # , retrying in 5 secs: {err}")
            raise err

    async def run_job(self, job_base: JobTemplate) -> ArgoWorkflowRun:
        if isinstance(job_base.inputs, list):
            jobs = []
            for i, inp in enumerate(job_base.inputs):
                job = deepcopy(job_base)
                job.custom_id = i + 1
                job.name = f"{job.name}-subjob-{i+1}"
                job.inputs = inp
                jobs.append(job)
        else:
            jobs = [job_base]

        template = self.template_generator.create(
            jobs=jobs,
            job_base=job_base,
        )

        config = self._get_job_config(job_base)

        return await self.submit(template, config.base.namespace, config.base.verify_ssl)

        # return template

    async def run_batch_jobs(self, job_base: JobTemplate, jobs: List[JobTemplate]) -> ArgoWorkflowRun:
        config = self._get_job_config(job_base)
        template = self.template_generator.create(
            jobs=jobs,
            job_base=job_base,
        )
        return await self.submit(template, config.base.namespace, config.base.verify_ssl)

    async def retry_workflow(self, workflow_id: WorkflowId):
        # @TODO: to be implemented
        pass

    async def resubmit(self, bucket_meta: BucketMeta, workflow_id: WorkflowId, namespace: str, verify_ssl=True):
        """
        Resubmit a workflow again.
        """
        obj = await self.get_workflow_template(bucket_meta, workflow_id, namespace)
        template = obj.model_dump(by_alias=True)
        template["metadata"] = {"generateName": obj.metadata.generate_name}
        template["apiVersion"] = "argoproj.io/v1alpha1"
        template["kind"] = "Workflow"

        if "jobs" in template:
            del template["jobs"]

        # return template

        return await self.submit(template, namespace, verify_ssl=verify_ssl)

    """
      #####
     #     # ###### #####
     #       #        #
     #  #### #####    #
     #     # #        #
     #     # #        #
      #####  ######   #

    """

    async def get_workflow(
        self,
        bucket_meta: BucketMeta,
        workflow_id: WorkflowId,
        output: bool = False,
        file_refs: bool = True,
        namespace: Optional[str] = "cmr-xt-argo",
    ) -> ArgoWorkflowRun:
        """
        :param user_id: is not required for argo workflows.
        """

        async def add_outputs(workflow: ArgoWorkflowRun):
            for i, node in enumerate(workflow.status.nodes):
                workflow.status.nodes[i] = await WorkflowService.add_data_to_argo_node(
                    node,
                    bucket_meta,
                    workflow.metadata.name,
                    self.template_generator.config.upload.loc_name,
                    output,
                    file_refs,
                )
            return workflow

        result = await self._get_workflow_only(workflow_id, namespace, bucket_meta)
        if result.is_found:
            return await add_outputs(result.workflow)

        raise NotFoundError(detail=f"Could not found the workflow: {workflow_id.name} from namespace: {namespace}")

    async def get_workflow_template(
        self,
        bucket_meta: BucketMeta,
        workflow_id: WorkflowId,
        namespace: str,
    ):
        raw_result = await self._get_workflow_only(workflow_id, namespace, bucket_meta=bucket_meta, get_raw_results=True)
        # return raw_result
        return self._format_workflow_resp(raw_result.workflow, fields=["spec", "metadata"])

    async def get_workflows_all(
        self,
        source: ArgoWorkflowStoreType,
        namespace: str,
        bucket_meta: Optional[BucketMeta] = None,
        has_details: bool = False,
    ) -> Union[List[str], List[ArgoWorkflowRun]]:
        """
        This async function retrieves all workflows based on the specified
        parameters and returns either a list of workflow names or a list of
        detailed workflow runs.

        :param source: The `source` parameter is used to specify the type of
        Argo workflow store to retrieve workflows from. It is an enumeration
        type with possible values of `LIVE` or `ARCHIVED`
        :type source: ArgoWorkflowStoreType

        :param namespace: The `namespace` parameter in the `get_workflows_all`
        function specifies the namespace in which to search for workflows. In
        Kubernetes, namespaces are used to organize and isolate resources within
        a cluster. In this case, the function will look for workflows specifically
        within the "cmr-xt-argo", defaults to cmr-xt-argo
        :type namespace: str (optional)

        :param bucket_meta: To make workflow functions independent of project set up,
        we pass BucketMeta object.
        :type bucket_meta: BucketMeta

        :param has_details: The `has_details` parameter is a boolean flag that
        indicates whether additional details should be included in the response for
        each workflow run. If `has_details` is set to `True`, the response will
        include more information about each workflow run. If it is set to `False`,
        the response will only, defaults to False
        :type has_details: bool (optional)
        """

        def format_list_workflows(response) -> List[ArgoWorkflowRun]:
            if response.status_code != 200:
                raise ApiException(status=response.status_code, reason=response.text)

            if "items" not in response.json():
                raise ApiException(status=response.status_code, reason=response.text)

            if has_details:
                return [self._format_workflow_resp(item) for item in response.json().get("items", [])]

            return [item.get("metadata").get("name") for item in response.json().get("items", [])]

        if source == ArgoWorkflowStoreType.LIVE:
            LOG.info("Getting Live Workflows.")
            return format_list_workflows(await self.api_get(f"workflows/{namespace}"))

        if source == ArgoWorkflowStoreType.ARCHIVE:
            LOG.info("Getting Archived Workflows.")
            return format_list_workflows(await self.api_get(f"archived-workflows?namespace={namespace}"))

        if source == ArgoWorkflowStoreType.STORAGE:
            storage = get_storage_client()
            folder_path = bucket_meta.base_path  # storage.get_standard_workflow_upload_path(bucket_id)

            LOG.info("Getting workflows from Storage.")

            workflow_names = await storage.get_immediate_folder_names(bucket_meta.name, folder_path)
            if has_details:
                lst_workflows = []
                for name in workflow_names:
                    wrk = await self._get_workflow_only(
                        workflow_id=WorkflowId(name=name),
                        namespace=namespace,
                        bucket_meta=bucket_meta,
                    )
                    lst_workflows.append(self._format_workflow_resp(wrk.workflow.model_dump()))

                return lst_workflows
            return workflow_names

        raise ValueError("Unacceptable source type.")

    async def _is_workflow_live(self, workflow_id: WorkflowId, namespace: str):
        try:
            res = await self._get_workflow_by_store_type(workflow_id, namespace, source=ArgoWorkflowStoreType.LIVE)
            LOG.info(f"Workflow: {workflow_id.name} exists in live records.")
            return True, res
        except Exception as e:
            return False, e

    async def _is_workflow_archived(self, workflow_id: WorkflowId, namespace: str):
        try:
            res = await self._get_workflow_by_store_type(workflow_id, namespace, source=ArgoWorkflowStoreType.ARCHIVE)
            LOG.info(f"Workflow: {workflow_id.name} exists in archive records.")
            return True, res
        except Exception as e:
            return False, e

    async def _is_workflow_stored(
        self,
        workflow_id: WorkflowId,
        namespace: str,
        bucket_meta: BucketMeta,
    ):
        try:
            res = await self._get_workflow_by_store_type(
                workflow_id,
                namespace,
                source=ArgoWorkflowStoreType.STORAGE,
                bucket_meta=bucket_meta,
            )
            LOG.info(f"Workflow: {workflow_id.name} exists in storage records.")
            return True, res
        except Exception as e:
            return False, e

    def _format_workflow_resp(self, resp, fields=["metadata", "status"]):
        resp_dict = resp if isinstance(resp, dict) else resp.json()

        if isinstance(resp_dict, dict):
            if "metadata" in resp_dict:
                return ArgoWorkflowRun.populate_from_res(resp_dict, fields)

            if "message" in resp_dict:
                raise NotFoundException(reason=resp_dict["message"])

        return resp

    async def _get_workflow_only(
        self,
        workflow_id: WorkflowId,
        namespace: str,
        bucket_meta: BucketMeta = None,
        get_raw_results: bool = False,
    ) -> GetWorkflowRes:
        """
        This methods goes through all sources where a workflow may be stored, i.e.:
        1. Live Records (mainly applicable when workflow is running)
        2. Archived Records (managed by Argo instance itself, but only lives for 1 week in EASI)
        3. Cloud Storage (Once workflow completed, a json copy of it is stored in the project
        folder.
        The location is project specific and depends on how it is configured.
        )
        """
        for source_type in ArgoWorkflowStoreType:
            try:
                res = await self._get_workflow_by_store_type(
                    workflow_id, namespace, source=source_type, get_raw_results=get_raw_results, bucket_meta=bucket_meta
                )
                LOG.info(f"Workflow: {workflow_id.name} exists in {source_type.value} records.")
                return GetWorkflowRes(workflow=res, is_found=True, source_type=source_type)
            except KeyError:
                LOG.info(f"Workflow: {workflow_id.name} does not exist in {source_type.value} records.")
            except Exception as e:
                LOG.info(f"Workflow: {workflow_id.name} does not exist in {source_type.value} records." f"Reason: {e}")

                #
        return GetWorkflowRes(workflow=None, is_found=False, source_type=None)

    async def _get_workflow_by_store_type(
        self,
        workflow_id: WorkflowId,
        namespace: str,
        source: ArgoWorkflowStoreType = ArgoWorkflowStoreType.LIVE,
        get_raw_results: bool = False,
        bucket_meta: Optional[BucketMeta] = None,
    ) -> ArgoWorkflowRun | Dict:
        """
        :param workflow_id: The id of the completed workflow from which you want to
        fetch log information. int is applicable for gitlab workflows. For argo, is
        either name or uuid.

        :param source: where to get the workflow from. If workflow is running, it
        should get from `workflows` endpoint. In this case, `workflow_id` is the
        workflow's unique name.

        If workflow completed, it should get from `archived-workflows` endpoint. In this case,
        `workflow_id` is the workflow's unique id (uid).

        If workflow is stored in storage (e.g. S3). Then, workflow name is used.

        :param bucket_meta: Usually, identifies the allocated folder for a specific user within
        a specific project. Unless, project is structured in another way.

        Note: when workflow is running, this parameter is useless as the logs are recieved live.
        """
        resp = None
        if source == ArgoWorkflowStoreType.LIVE:
            resp = await self.api_get(f"workflows/{namespace}/{workflow_id.name}")

        if source == ArgoWorkflowStoreType.ARCHIVE:
            resp = await self.api_get(f"archived-workflows/{workflow_id.uid}?namespace={namespace}")

        if source == ArgoWorkflowStoreType.STORAGE:
            # st = get_settings()
            storage = get_storage_client()
            # upload_base_path = storage.get_standard_workflow_upload_path(bucket_id)
            file_path = f"{bucket_meta.base_path}/{workflow_id.name}/workflow.json"

            workflow_file = await storage.get_file(bucket_meta.name, file_path)

            resp = json.loads(workflow_file.read().decode("utf-8"))

        if get_raw_results:
            return resp

        response = self._format_workflow_resp(resp)
        if response is not None:
            return response

        raise NotFoundError(detail=f"Could not found the workflow: {workflow_id.name} from namespace: {namespace}")

    #
    #        ####   ####   ####
    #       #    # #    # #
    #       #    # #       ####
    #       #    # #  ###      #
    #       #    # #    # #    #
    #######  ####   ####   ####

    async def get_workflow_log(
        self,
        workflow_id: WorkflowId,
        bucket_meta: BucketMeta,
        namespace: str | None = None,
    ):
        """
        This method is used to retrieve logs for a specific workflow.
        """

        if workflow_id.name is None:
            raise ValueError("Workflow unique name must be provided.")

        # Check workflow is Live
        is_live, workflow = await self._is_workflow_live(workflow_id, namespace)

        # Get Live
        live_logs = {}
        if is_live and (workflow.status.phase.upper() == JobStatus.RUNNING or workflow.status.phase.upper() == JobStatus.PENDING):
            LOG.info("Getting live logs...")
            try:
                res = await self.api_get(f"workflows/{namespace}/{workflow_id.name}/log?logOptions.container=main")
                live_logs = self._format_live_log(res)
                if isinstance(live_logs, dict):
                    LOG.info(f"Number of logs from Live: {len(live_logs.keys())}")

            except ForbiddenException as ex:
                LOG.error(f"Workflow: {workflow_id.name} is yet live, but log is not accessible")
                raise ForbiddenException(f"Workflow: {workflow_id.name} is yet live, but log is not accessible") from ex
            # Handle if it's yet live but not found
        else:
            is_archived, workflow = await self._is_workflow_archived(workflow_id, namespace)
            if not is_archived:
                is_stored, workflow = await self._is_workflow_stored(workflow_id, namespace, bucket_meta)
                if not is_stored:
                    LOG.error(f"Workflow: {workflow_id.name} was not found.")
                    raise NotFoundException(f"Workflow: {workflow_id.name} was not found.")

        # Get from Storage
        storage = get_storage_client()
        # st = get_settings()
        stored_logs = {}

        LOG.info("Getting stored log...")
        for node in workflow.status.nodes:
            try:
                if node.type.lower() == "pod" and node.template_name in self.template_generator.config.logs_to_include:
                    node.set_pod_task_names()
                    if node.pod_name not in live_logs:
                        file_path = f"{bucket_meta.base_path}/{workflow_id.name}/{node.pod_name}/main.log"
                        # file_path = storage.add_project_base_path(
                        #     bucket_id,
                        #     f"{st.WORKFLOW_UPLOAD_PATH}/{workflow_id.name}/{node.pod_name}/main.log",
                        # )
                        log_file = await storage.get_file(bucket_meta.name, file_path)
                        if log_file:
                            stored_logs[node.pod_name] = log_file.read().decode("utf-8")
            except ForbiddenException as err:
                LOG.error(f"Was not able to access the log for {node.pod_name} from storage. {err}")

        LOG.info(f"Number of logs from storage: {len(stored_logs.keys())}")
        stored_logs.update(live_logs)
        return stored_logs
        #     return stored_logs
        # except Exception as e:
        #     raise ValueError(f"Was not able to access the log for {node.pod_name} from storage.")

    async def get_job_log(
        self,
        job_id: Union[int, str],
        workflow_id: WorkflowId = None,
    ):
        # @TODO: is it yet needed? Logs for all jobs are included in `get_workflow_log`
        pass

    @classmethod
    def _format_live_log(cls, res):
        try:
            json_objects = res.text.strip().split("\n")
            logs = {}
            for json_obj in json_objects:
                obj = json.loads(json_obj)
                key = obj["result"]["podName"]
                val = obj["result"]["content"]
                if key in logs:
                    logs[key] += val + "\n"
                else:
                    logs[key] = val
            return logs
        except Exception:
            LOG.warning(f"Log is not in the expected format: {res.text}")
            return res.text

    ######
    #     # ###### #      ###### ##### ######
    #     # #      #      #        #   #
    #     # #####  #      #####    #   #####
    #     # #      #      #        #   #
    #     # #      #      #        #   #
    ######  ###### ###### ######   #   ######

    async def delete_workflow(
        self,
        bucket_meta: BucketMeta,
        workflow_id: WorkflowId,
        namespace: str,
        force_data_delete: Optional[bool] = False,
    ) -> bool:
        if await self._delete_workflow_clean_up(bucket_meta, workflow_id, namespace):
            return await self._delete_workflow_only(bucket_meta, workflow_id, namespace)
        return False

    async def _delete_workflow_only(
        self,
        bucket_meta: BucketMeta,
        workflow_id: Union[int, str, WorkflowId],
        namespace: str,
    ) -> bool:
        """
        This method only deletes the workflow meta data record. It wouldn't clean up
        the files associated to the workflow.
        """
        # Delete Workflow from LIVE records.
        is_running, _ = await self._is_workflow_live(workflow_id, namespace)
        if is_running:
            try:
                # Using force delete, as most of the time a normal delete does not work!
                await self.api_delete(f"workflows/{namespace}/{workflow_id.name}?force=true")
                LOG.info(f"Workflow: {workflow_id.name} deleted from workflows records.")
            except Exception as e:
                LOG.warning(f"Error in deleting workflow: {workflow_id.name} from workflows records. {e}")

        # Delete Archived Workflow
        is_archived, _ = await self._is_workflow_archived(workflow_id, namespace)
        if is_archived:
            try:
                # Using force delete, as most of the time a normal delete does not work!
                await self.api_delete(f"archived-workflows/{workflow_id.uid}?namespace={namespace}")
                LOG.info(f"Workflow: {workflow_id.name} deleted from archived workflow records.")
            except Exception as e:
                LOG.warning(f"Error in deleting workflow: {workflow_id.name} from archived workflows. {e}")

        # Delete Workflow from STORAGE -@TODO ?
        is_stored, _ = await self._is_workflow_stored(workflow_id, namespace, bucket_meta)
        if is_stored:
            storage = get_storage_client()
            file_path = f"{bucket_meta.base_path}/{workflow_id.name}/workflow.json"
            await storage.delete_file(bucket_meta.name, file_path, True)

        # Check if workflow yet exist
        try:
            workflow = await self.get_workflow(bucket_meta, workflow_id, file_refs=False, namespace=namespace)
            if workflow.metadata.uid == workflow_id.uid:
                LOG.info(f"Workflow: {workflow_id.name} still exists in the records after deletion attempts!")
                return False
        except Exception:
            LOG.info(f"Workflow: {workflow_id.name} deleted from all records.")
        return True

    async def _delete_workflow_clean_up(
        self, bucket_meta: BucketMeta, workflow_id: Union[int, str, WorkflowId], namespace: str, verify_ssl: bool = True
    ) -> bool:
        """
        This methods aims to clean up all files associated with the workflow.
        """

        # Delete Artifacts
        LOG.info("Initiating deleting artifacts.")
        res_art_del = await self._delete_workflow_artifacts(workflow_id.name, namespace, verify_ssl)
        if res_art_del.metadata.name is None:
            LOG.info(f"An error occured when submitting the workflow to delete " f"the artifacts for workflow: {workflow_id.name}")
            return False
        else:
            LOG.info(f"Deleting Artifacts successfully submitted for workflow: {workflow_id.name}.")

        # Delete bucket
        try:
            LOG.info(f"Deleting all output files and data related to workflow: " f"{workflow_id.name} from database.")
            storage = get_storage_client()
            folder_path = f"{bucket_meta.base_path}/{workflow_id.name}"
            # storage.add_project_base_path(bucket_id, f"{get_settings().WORKFLOW_UPLOAD_PATH}/{workflow_id.name}")
            LOG.info(f"folder_path: {folder_path}")
            await storage.delete_file(bucket_meta.name, folder_path, True)
        except Exception as e:
            LOG.warning(f"An error occured when trying to delete output data of workflow: " f"{workflow_id.name}: {e}")
            return False

        return True

    async def _delete_workflow_artifacts(self, workflow_id: Union[int, str], namespace: str, verify_ssl: bool = True):
        """
        :param workflow_id: is the unique name of the workflow.
        """
        manifest = self.template_generator.delete_workflow_artifacts(workflow_uname=workflow_id)
        return await self.submit(manifest, namespace, verify_ssl)

    ######                             #                #     #
    #     #   ##    ####  ######      # #   #####  #    ##   ## ###### ##### #    #  ####  #####   ####
    #     #  #  #  #      #          #   #  #    # #    # # # # #        #   #    # #    # #    # #
    ######  #    #  ####  #####     #     # #    # #    #  #  # #####    #   ###### #    # #    #  ####
    #     # ######      # #         ####### #####  #    #     # #        #   #    # #    # #    #      #
    #     # #    # #    # #         #     # #      #    #     # #        #   #    # #    # #    # #    #
    ######  #    #  ####  ######    #     # #      #    #     # ######   #   #    #  ####  #####   ####

    def gen_api_endpoint(self, route):
        """
        returns back api endpoint for argo.
        """
        return f"{self.api_url}/{route}"

    async def api_get(self, route, verify_ssl=True):
        """
        handles get request to argo's api.
        """
        async with httpx.AsyncClient(verify=verify_ssl) as client:
            return await client.get(self.gen_api_endpoint(route), headers=self.api_headers)

    async def api_delete(self, route, verify_ssl=True):
        """
        handles delete request to argo's api.
        """
        if verify_ssl:
            async with httpx.AsyncClient() as client:
                return await client.delete(self.gen_api_endpoint(route), headers=self.api_headers)

        async with httpx.AsyncClient(verify=verify_ssl) as client:
            return await client.delete(
                self.gen_api_endpoint(route),
            )

    async def api_put(self, route, body={}, verify_ssl=True):
        """
        handles update request to argo's api.
        """
        if verify_ssl:
            async with httpx.AsyncClient() as client:
                return await client.put(self.gen_api_endpoint(route), json=body, headers=self.api_headers)

        async with httpx.AsyncClient(verify=verify_ssl) as client:
            return await client.put(self.gen_api_endpoint(route), json=body)

    async def api_post(self, route, body={}, verify_ssl=True):
        """
        handles post request to argo's api.
        """
        if verify_ssl:
            async with httpx.AsyncClient() as client:
                return await client.post(self.gen_api_endpoint(route), json=body, headers=self.api_headers)

        async with httpx.AsyncClient(verify=verify_ssl) as client:
            return await client.post(self.gen_api_endpoint(route), json=body)
