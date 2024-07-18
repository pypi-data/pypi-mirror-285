"""
Description: This script is the main script to generate argo workflow templates.

Author: Ben Motevalli (benyamin.motevalli@csiro.au)
Created: 2023-11-07
"""

import json
import os
from typing import List, Optional, Union

import yaml
from jinja2 import BaseLoader, Environment

from fa_common import get_settings
from fa_common.enums import WorkflowEnums
from fa_common.exceptions import UnImplementedError

from .enums import CloudBaseImage
from .models import ArgoTemplateConfig, JobTemplate


def str_presenter(dumper, data):
    """
    multiline in yaml.
    """
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_presenter)
# to use with safe_dump:
yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


dirname = os.path.dirname(__file__)


class ArgoTemplateGenerator:
    #####  ####### #     # ####### ###  #####
    #     # #     # ##    # #        #  #     #
    #       #     # # #   # #        #  #
    #       #     # #  #  # #####    #  #  ####
    #       #     # #   # # #        #  #     #
    #     # #     # #    ## #        #  #     #
    #####  ####### #     # #       ###  #####

    config: ArgoTemplateConfig = ArgoTemplateConfig()
    jinja_env: Environment = Environment(
        variable_start_string="<<",
        variable_end_string=">>",
        block_start_string="<%",
        block_end_string="%>",
        loader=BaseLoader(),
    )

    def set_config(self, config: ArgoTemplateConfig):
        """
        Set the configuration for generating Argo templates.

        Parameters:
            config (ArgoTemplateConfig): The configuration object to use.
        """
        if not isinstance(config, ArgoTemplateConfig):
            raise ValueError("config must be an instance of ArgoTemplateConfig")
        self.config = config

    ######  ######  #######    #    ####### #######
    #     # #     # #         # #      #    #
    #       #     # #        #   #     #    #
    #       ######  #####   #     #    #    #####
    #       #   #   #       #######    #    #
    #     # #    #  #       #     #    #    #
    ######  #     # ####### #     #    #    #######

    @classmethod
    def create(
        cls,
        jobs: List[JobTemplate],
        job_base: JobTemplate,
        # workflow_callbacks: List[WorkflowCallBack] = [],
        # has_upload: Optional[bool] = True,
    ):
        """
        @AddMe: Handle None checks.
        """
        has_upload = job_base.uploads is not None
        config = cls.config if job_base.template_config is None else job_base.template_config
        base_template = cls.gen_base_block(job_base, config)
        run_template = cls.gen_run_template(job_base, config, has_upload)
        main_template = cls.gen_tasks_main_template(jobs, config, has_upload)
        arch_template = cls.get_archive_template(job_base, config)

        base_template["spec"]["templates"] = [main_template]
        if not config.run.is_unified:
            download_template = cls.gen_download_template(config)
            base_template["spec"]["templates"].append(download_template)

        base_template["spec"]["templates"].append(run_template)
        base_template["spec"]["templates"].append(arch_template)

        if has_upload:
            upload_template = cls.gen_upload_template(jobs, config)
            base_template["spec"]["templates"].append(upload_template)

        return base_template

    #    ###### ####### ######     ####### ####### #     # ######  #          #    ####### #######
    #    #     # #     #       #    #       ##   ## #     # #         # #      #    #
    #    #     # #     #       #    #       # # # # #     # #        #   #     #    #
    #    #     # ######        #    #####   #  #  # ######  #       #     #    #    #####
    #    #     # #             #    #       #     # #       #       #######    #    #
    #    #     # #             #    #       #     # #       #       #     #    #    #
    #    ####### #             #    ####### #     # #       ####### #     #    #    #######

    @classmethod
    def gen_base_block(cls, job_base: JobTemplate, config: ArgoTemplateConfig):
        """
        This function creates the base-top block of the manifest.
        Most contents in this block are common.
        """
        # FIXME: Check with Sam. This might overlap with MINIO secrets.
        # @REVIEW

        settings = get_settings()
        params = {
            "NAME": f"{job_base.name}",
            "SECRET_NAME": settings.STORAGE_SECRET_NAME,
            # "HAS_SECRET": config.has_secret,
            "IS_LOCAL": config.base.is_argo_local,
            "ARCHIVE_TEMP_NAME": WorkflowEnums.Templates.ARCHIVE.value,
            "IMAGE_PULL_SECRETS": job_base.module.version.module_meta.image_ref.image_pull_secrets,
            "SERVICE_ACCOUNT_NAME": config.base.service_account_name,
        }

        return cls._populate_template_block("template_base.yaml", params)

    @classmethod
    def get_archive_template(cls, job_base: JobTemplate, config: ArgoTemplateConfig):
        """
        Handles archive template
        """
        settings = get_settings()
        argo_url = settings.ARGO_URL
        if config.base.is_argo_local:
            argo_url = settings.ARGO_URL.replace("localhost", "host.docker.internal")
        if len(job_base.callbacks) > 0:
            for callback in job_base.callbacks:
                if "localhost" in callback.url:
                    callback.url = callback.url.replace("localhost", "host.docker.internal")

        params = {
            "ARCHIVE_TEMP_NAME": WorkflowEnums.Templates.ARCHIVE.value,
            "IS_ERR_TOLER": config.base.is_error_tolerant,
            "SECRET_NAME": config.upload.access_secret_name,
            "SECRET_KEY": config.upload.access_secret_key,
            "HAS_SECRET": config.upload.has_secret,
            "STORAGE_TYPE": settings.STORAGE_TYPE,
            "STORAGE_ENUM": WorkflowEnums.FileAccess.STORAGE,
            "CLOUD_BASE_IMAGE": config.upload.cloud_base_image,
            "UPLOAD_BASE_PATH": job_base.uploads.default_path,
            "HAS_ARGO_TOKEN": config.base.has_argo_token,
            "ARGO_BASE_URL": argo_url,
            "IS_LOCAL": config.base.is_argo_local,
            "NAMESPACE": settings.ARGO_NAMESPACE,
            "HAS_WORKFLOW_CALLBACKS": len(job_base.callbacks) > 0,
            "WORKFLOW_CALLBACKS": job_base.callbacks,
        }

        return cls._populate_template_block("template_archive_workflow.yaml", params)

    ######  ####### #     # #     # #       #######    #    ######
    #     # #     # #  #  # ##    # #       #     #   # #   #     #
    #     # #     # #  #  # # #   # #       #     #  #   #  #     #
    #     # #     # #  #  # #  #  # #       #     # #     # #     #
    #     # #     # #  #  # #   # # #       #     # ####### #     #
    #     # #     # #  #  # #    ## #       #     # #     # #     #
    ######  #######  ## ##  #     # ####### ####### #     # ######

    @classmethod
    def gen_download_template(cls, config: ArgoTemplateConfig):
        """
        Generate Download Template
        """
        if config.download.access_method == WorkflowEnums.FileAccess.Method.SIGNED_URL:
            raise UnImplementedError("Signed url for downloading files is not yet implemented.")

        if config.download.access_method is None:
            raise ValueError(
                "Download access method and storage type should be defined."
                + "Make sure config parameters (file_access_method, file_cloud_storage) are set."
            )

        settings = get_settings()

        params = {
            "TEMPLATE_NAME": WorkflowEnums.Templates.DOWNLOAD.value,
            "IS_ERR_TOLER": config.base.is_error_tolerant,
            "SECRET_NAME": config.download.access_secret_name,
            "SECRET_KEY": config.download.access_secret_key,
            "HAS_SECRET": config.download.has_secret,
            "STORAGE_TYPE": settings.STORAGE_TYPE,
            "STORAGE_ENUM": WorkflowEnums.FileAccess.STORAGE,
            "STORAGE_ENDPOINT_URL": settings.STORAGE_ENDPOINT,
            "DOWNLOAD_LOGGING": config.download.save_logs,
            "CLOUD_BASE_IMAGE": config.download.cloud_base_image,
        }

        return cls._populate_template_block("template_download.yaml", params)

    ######  #     # #     #    #     # ####### ######  #######
    #     # #     # ##    #    ##    # #     # #     # #
    #     # #     # # #   #    # #   # #     # #     # #
    ######  #     # #  #  #    #  #  # #     # #     # #####
    #   #   #     # #   # #    #   # # #     # #     # #
    #    #  #     # #    ##    #    ## #     # #     # #
    #     #  #####  #     #    #     # ####### ######  #######

    @classmethod
    def gen_run_template(
        cls,
        job_base: JobTemplate,
        config: ArgoTemplateConfig,
        has_upload: bool = True,
        # image_url: Optional[str] = None,
        # run_command: Optional[str] = None,
        # cpu: Optional[Union[int,str]] = None,
        # memory: Optional[str] = None,
        # max_dependency: Optional[int] = 0
    ):
        """
        Generate Run Template
        """
        if config.run.strategy is None:
            raise ValueError("Running strategy is not set!")

        settings = get_settings()

        module_meta_base = job_base.module.version.module_meta
        version = job_base.module.version.name
        image = f"{module_meta_base.image_ref.url}:{version}"
        params = {
            "SECRET_NAME": config.download.access_secret_name,
            "SECRET_KEY": config.download.access_secret_key,
            "HAS_SECRET": config.download.has_secret,
            "STORAGE_TYPE": settings.STORAGE_TYPE,
            "STORAGE_ENUM": WorkflowEnums.FileAccess.STORAGE,
            "STORAGE_ENDPOINT_URL": settings.STORAGE_ENDPOINT,
            "CLOUD_BASE_IMAGE": config.download.cloud_base_image,
            "IS_ERR_TOLER": config.base.is_error_tolerant,
            "MAX_NUM": config.run.max_all_jobs_dependency,
            "HAS_UPLOAD": has_upload,
            "JOB": job_base,
            "IMG_PULL_POLICY": module_meta_base.image_ref.image_pull_policy.value,
            "APP_INPUT_PATH": module_meta_base.image_ref.run_meta.input_path,
            "APP_PRE_COMMAND": config.run.commands_pre,
            "APP_MAIN_COMMAND": module_meta_base.image_ref.run_meta.cmd,
            "APP_POST_COMMAND": config.run.commands_post,
            "APP_OUTPUT_PATH": module_meta_base.image_ref.run_meta.output_path,
            "ENV_SECRETS": module_meta_base.image_ref.env_secrets,
            "MOUNT_SECRETS": module_meta_base.image_ref.mount_secrets,
            "ENV_CONFIGS": module_meta_base.image_ref.env_configs,
            "ENV_VARS": job_base.env_vars,
            "MEM_REQ": job_base.resources.mem_req,
            "MEM_LIM": job_base.resources.mem_limit,
            "CPU_REQ": job_base.resources.cpu_req,
            "CPU_LIM": job_base.resources.cpu_limit,
            "IMAGE_URL": image,
        }

        if config.run.strategy == WorkflowEnums.Run.Strategy.GLOBAL:
            return cls._populate_template_block("template_run_global.yaml", params)

        if config.run.strategy == WorkflowEnums.Run.Strategy.NODAL:
            return cls._populate_template_block("template_run_nodal.yaml", params)

        if config.run.strategy == WorkflowEnums.Run.Strategy.UNI_GLOBAL:
            return cls._populate_template_block("unified_template_run_global.yaml", params)

        if config.run.strategy == WorkflowEnums.Run.Strategy.UNI_NODAL:
            return cls._populate_template_block("unified_template_run_nodal.yaml", params)

        raise ValueError("Running strategy is unknown in the workflow!")

    #     # ######  #       #######    #    ######     #     # ####### ######  #######
    #     # #     # #       #     #   # #   #     #    ##    # #     # #     # #
    #     # #     # #       #     #  #   #  #     #    # #   # #     # #     # #
    #     # ######  #       #     # #     # #     #    #  #  # #     # #     # #####
    #     # #       #       #     # ####### #     #    #   # # #     # #     # #
    #     # #       #       #     # #     # #     #    #    ## #     # #     # #
    ######  #       ####### ####### #     # ######     #     # ####### ######  #######

    @classmethod
    def gen_upload_template(cls, jobs: List[JobTemplate], config: ArgoTemplateConfig):
        """
        Generate Upload Templates
        """
        if config.upload.strategy is None:
            raise ValueError(
                "Upload strategy and storage type should be defined."
                + "Make sure config parameters (upload_strategy, file_cloud_storage) are set."
            )

        settings = get_settings()

        params = {
            "TEMPLATE_NAME": WorkflowEnums.Templates.UPLOAD.value,
            "IS_ERR_TOLER": config.base.is_error_tolerant,
            "SECRET_NAME": config.upload.access_secret_name,
            "SECRET_KEY": config.upload.access_secret_key,
            "STORAGE_ENDPOINT_URL": settings.STORAGE_ENDPOINT,
            "HAS_SECRET": config.upload.has_secret,
            "STORAGE_TYPE": settings.STORAGE_TYPE,
            "STORAGE_ENUM": WorkflowEnums.FileAccess.STORAGE,
            "UPLOAD_LOGGING": config.upload.save_logs,
            "RUN_LOGGING": config.run.save_logs,
            "CLOUD_BASE_IMAGE": config.upload.cloud_base_image,
        }

        if config.upload.strategy == WorkflowEnums.Upload.Strategy.EVERY:
            return cls._populate_template_block("template_upload_every.yaml", params)

        if config.upload.strategy == WorkflowEnums.Upload.Strategy.ONE_GO:
            params["JOBS"] = jobs
            return cls._populate_template_block("template_upload_one_go.yaml", params)

    #     #                    #######
    ##   ##   ##   # #    #       #      ##    ####  #    #  ####
    # # # #  #  #  # ##   #       #     #  #  #      #   #  #
    #  #  # #    # # # #  #       #    #    #  ####  ####    ####
    #     # ###### # #  # #       #    ######      # #  #        #
    #     # #    # # #   ##       #    #    # #    # #   #  #    #
    #     # #    # # #    #       #    #    #  ####  #    #  ####

    @classmethod
    def gen_tasks_main_template(cls, jobs: List[JobTemplate], config: ArgoTemplateConfig, has_upload: Optional[bool] = True):
        """
        Generate Main Tasks
        """
        is_nodal = config.run.strategy == WorkflowEnums.Run.Strategy.NODAL

        tasks_temp = []
        tasks = []
        for i, job in enumerate(jobs):
            job_name = cls._gen_internal_job_name(job.custom_id)
            module_meta = job.module.version.module_meta
            version = job.module.version.name
            image = f"{module_meta.image_ref.url}:{version}"
            task = {
                "INDEX": i,
                "DOWNLOAD_TASK_NAME": f"download-files-{job.custom_id}",
                "DOWNLOAD_TEMPLATE_NAME": WorkflowEnums.Templates.DOWNLOAD.value,
                "DOWNLOAD_FILES": json.dumps(json.dumps([file_ref.model_dump() for file_ref in job.inputs.files])),
                "DOWNLOAD_REQUIRED": len(job.inputs.files) > 0,
                "RUN_TASK_NAME": job_name,
                "RUN_TASK_CUSTOM_ID": job.custom_id,
                "RUN_TEMPLATE_NAME": WorkflowEnums.Templates.RUN.value,
                "RUN_INPUT_PARAMS": job.inputs.parameters,
                "RUN_HAS_DEPENDENCY": len(job.dependency) > 0,
                "RUN_CONTINUE_ON": config.base.continue_on_run_task_failure,
                "RUN_LIST_DEPENDENCY": [
                    {
                        "INDEX": ii,
                        "PAR_JOB_NAME": cls._gen_internal_job_name(par_custom_id),
                        "PAR_JOB": cls._get_job(jobs, par_custom_id),
                        "ART_NAME": cls._get_dependency_artifact_name(ii)[1],
                        "LOC_NAME": cls._get_dependency_artifact_name(ii)[0],
                    }
                    for ii, par_custom_id in enumerate(job.dependency)
                ],
                "RUN_NODAL_PARAMS": (
                    [
                        {"NAME": "IMAGE", "VALUE": image},
                        {"NAME": "MEM_REQ", "VALUE": job.resources.mem_req},
                        {"NAME": "CPU_REQ", "VALUE": job.resources.cpu_req},
                        {"NAME": "MEM_LIM", "VALUE": job.resources.mem_limit},
                        {"NAME": "CPU_LIM", "VALUE": job.resources.cpu_limit},
                        {"NAME": "COMMAND", "VALUE": module_meta.image_ref.run_meta.cmd},
                        {"NAME": "PRE_COMMAND", "VALUE": config.run.commands_pre},
                        {"NAME": "POST_COMMAND", "VALUE": config.run.commands_post},
                    ]
                    if is_nodal
                    else []
                ),
                "UPLOAD_TASK_NAME": f"upload-{job.custom_id}",
                "UPLOAD_TEMPLATE_NAME": WorkflowEnums.Templates.UPLOAD.value,
                "UPLOAD_BASE_PATH": job.uploads.default_path,
                "UPLOAD_COPY_PATHS": json.dumps(job.uploads.copy_paths),
                "UPLOAD_CUSTOM_PATH": job.uploads.custom_path,
                "SELECTED_UPLOAD_OBJECTS": job.uploads.selected_outputs,
            }

            # DOWNLOAD, RUN, UPLOAD -> ONE NODE
            if config.run.is_unified:
                if task["RUN_HAS_DEPENDENCY"]:
                    tasks_temp.append(cls._populate_template_block("unified_task_run_chained.yaml", {"TASK": task}))
                else:
                    tasks_temp.append(cls._populate_template_block("unified_task_run_single.yaml", {"TASK": task}))
                continue

            # DOWNLOAD, RUN, UPLOAD -> SEPARATE NODES
            if task["DOWNLOAD_REQUIRED"]:
                tasks_temp.append(cls._populate_template_block("task_download.yaml", {"TASK": task}))

            if task["RUN_HAS_DEPENDENCY"]:
                tasks_temp.append(cls._populate_template_block("task_run_chained.yaml", {"TASK": task}))
            else:
                tasks_temp.append(cls._populate_template_block("task_run_single.yaml", {"TASK": task}))

            if has_upload and config.upload.strategy == WorkflowEnums.Upload.Strategy.EVERY:
                tasks_temp.append(cls._populate_template_block("task_upload_every.yaml", {"TASK": task}))

            tasks.append(task)

        # UPLOAD STRATEGY -> ONCE ALL JOBS COMPLETED
        # NOT IMPLEMENTED FOR UNIFIED
        if has_upload and config.upload.strategy == WorkflowEnums.Upload.Strategy.ONE_GO:
            if config.run.is_unified:
                raise UnImplementedError("One go upload is not implmented for Unified Nodes.")
            tasks_temp.append(cls._populate_template_block("task_upload_one_go.yaml", {"TASKS": tasks}))

        # return TASKS
        return {"name": "main", "dag": {"tasks": tasks_temp}}

    ######                                       #######
    #     # ###### #      ###### ##### ######       #    ###### #    # #####  #        ##   ##### ######
    #     # #      #      #        #   #            #    #      ##  ## #    # #       #  #    #   #
    #     # #####  #      #####    #   #####        #    #####  # ## # #    # #      #    #   #   #####
    #     # #      #      #        #   #            #    #      #    # #####  #      ######   #   #
    #     # #      #      #        #   #            #    #      #    # #      #      #    #   #   #
    ######  ###### ###### ######   #   ######       #    ###### #    # #      ###### #    #   #   ######

    @classmethod
    def delete_workflow_artifacts(cls, workflow_uname: str):
        """
        Generates template block to delete workflow's artifact.
        """
        manifest = cls._get_template_block(
            "workflow_delete_artifacts.yaml",
            temp_format=WorkflowEnums.TemplateFormats.YAML,
        )
        manifest["spec"]["arguments"]["parameters"][0]["value"] = workflow_uname
        manifest["spec"]["templates"][0]["image"] = CloudBaseImage.AWS
        manifest["spec"]["serviceAccountName"] = cls.config.base.service_account_name
        return manifest

    #     #
    #     # ###### #      #####  ###### #####   ####
    #     # #      #      #    # #      #    # #
    ####### #####  #      #    # #####  #    #  ####
    #     # #      #      #####  #      #####       #
    #     # #      #      #      #      #   #  #    #
    #     # ###### ###### #      ###### #    #  ####

    @classmethod
    def _gen_internal_job_name(cls, custom_id: Union[str, int]):
        return f"task-{custom_id}"

    @classmethod
    def _get_job(cls, jobs: List[JobTemplate], custom_id: Union[str, int]):
        job = list(filter(lambda job: job.custom_id == custom_id, jobs))

        if len(job) == 1:
            return job[0]
        raise ValueError(f"Cannot get a unique job with provided id: {custom_id}")

    @classmethod
    def _get_dependency_artifact_name(cls, index: int):
        loc_name = f"dep-art-loc-{index + 1}"
        art_name = f"dep-art-{index + 1}"
        return loc_name, art_name

    @classmethod
    def manifest_to_yaml(cls, template, filename=None):
        """
        Converts workflow template to yaml.
        """
        if filename is None:
            filename = f"{template['metadata']['generateName']}.yaml"

        with open(filename, "w") as outfile:
            yaml.dump(template, outfile)

    @classmethod
    def yaml_to_manifest(cls, yaml_path):
        """
        Converts a yaml file to workflow template.
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @classmethod
    def _get_template_block(
        cls,
        name: str,
        temp_format: WorkflowEnums.TemplateFormats = WorkflowEnums.TemplateFormats.TEXT,
    ):
        """
        Gets yaml template from `argo-templates` folder and returns it in different formats.
        """
        if temp_format == WorkflowEnums.TemplateFormats.YAML:
            return ArgoTemplateGenerator.yaml_to_manifest(os.path.join(dirname, f"argo-templates/{name}"))

        if temp_format == WorkflowEnums.TemplateFormats.TEXT:
            with open(os.path.join(dirname, f"argo-templates/{name}"), "r", encoding="utf-8") as f:
                return f.read()

        raise ValueError("Unknown template format.")

    @classmethod
    def _populate_template_block(cls, name: str, parameters: dict):
        """
        Pass the name of template and its parameters and get back the populated template.
        """
        template_txt = cls._get_template_block(name, temp_format=WorkflowEnums.TemplateFormats.TEXT)
        template_jin = cls.jinja_env.from_string(template_txt)
        return yaml.safe_load(template_jin.render(parameters))
