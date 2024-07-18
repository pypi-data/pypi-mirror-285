import json
import os
import shutil
import tempfile
import zipfile
from enum import Enum
from io import BytesIO
from typing import List, Optional

import yaml
from kube_watch.models.workflow import WorkflowConfig, WorkflowOutput
from prefect import get_run_logger, runtime

from fa_common.models import CamelModel, File
from fa_common.routes.modules.enums import ModuleRunModes
from fa_common.storage import get_storage_client
from fa_common.workflow.models import JobTemplate, WorkflowId

dirname = os.path.dirname(__file__)


class FileType(str, Enum):
    JSON = "json"
    YAML = "yaml"
    TXT = "txt"


# ========================================================
#     # ####### #       ######  ####### ######   #####
#     # #       #       #     # #       #     # #     #
#     # #       #       #     # #       #     # #
####### #####   #       ######  #####   ######   #####
#     # #       #       #       #       #   #         #
#     # #       #       #       #       #    #  #     #
#     # ####### ####### #       ####### #     #  #####
# ========================================================


def delete_directory(dir_path):
    """
    Deletes a directory along with all its contents.

    Args:
    dir_path (str): Path to the directory to be deleted.
    """
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} does not exist.")
        return

    try:
        shutil.rmtree(dir_path)
        print(f"Directory {dir_path} has been deleted successfully.")
    except Exception as e:
        print(f"Failed to delete {dir_path}. Reason: {e}")


# from config import ModuleSettings, set_global_settings


def ensure_directories_exist(directories):
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist, creating...")
            os.makedirs(directory, exist_ok=True)  # The exist_ok=True flag prevents raising an error if the directory already exists.
            print(f"Directory {directory} created.")
        else:
            print(f"Directory {directory} already exists.")


def write_storage_files(file_content: BytesIO, target_path: str, filename: str):
    with open(os.path.join(target_path, filename), "wb") as file:
        file_content.seek(0)
        file.write(file_content.read())


def extract_zip_from_bytesio(file_content: BytesIO, target_path: str):
    file_content.seek(0)
    with zipfile.ZipFile(file_content, "r") as zip_ref:
        # Iterate over all the files and directories in the zip file
        for member in zip_ref.namelist():
            # Determine the full local path of the file
            file_path = os.path.normpath(os.path.join(target_path, member))

            # Check if the file has a directory path, if it does, create the directory
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # If the current member is not just a directory
            if not member.endswith("/"):
                # Open the zip file member, create a corresponding local file
                source = zip_ref.open(member)
                with open(file_path, "wb") as target:
                    shutil.copyfileobj(source, target)
                source.close()

    print("Extraction complete.")


def copy_directory(src, dest, ignore_dirs=["venv", ".venv", "__pycache__"]):
    """
    Copies all files and directories from src to dest, ignoring specified directories.

    Args:
    src (str): Source directory path.
    dest (str): Destination directory path.
    ignore_dirs (list): Directories to ignore.

    """
    if not os.path.exists(dest):
        os.makedirs(dest)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            if item not in ignore_dirs:
                copy_directory(s, d, ignore_dirs)
        else:
            shutil.copy2(s, d)


async def init_working_directory(ignore_dirs=["venv", ".venv", "__pycache__"]):
    logger = get_run_logger()
    config = runtime.flow_run.parameters
    module_runner = f"{config.get('module_path')}/{config.get('module_version')}"

    if config.get("use_tmp_dir"):
        working_dir = config.get("tmp_dir")
        copy_directory(module_runner, working_dir, ignore_dirs)
    else:
        working_dir = os.path.join(module_runner, runtime.flow_run.id)

    logger.info(working_dir)
    runtime.flow_run.parameters["working_dir"] = working_dir
    chk_dirs = [
        working_dir,
        os.path.join(working_dir, config.get("input_path")),
        os.path.join(working_dir, config.get("output_path")),
    ]
    ensure_directories_exist(chk_dirs)


async def download_files(work_dir, sub_dir, sources: List[dict]):
    """
    The function `download_files` downloads files from a storage client and writes them to a specified
    directory.

    :param work_dir: The `work_dir` parameter represents the directory where the downloaded files will
    be stored. It is the main directory where the `sub_dir` will be created to store the downloaded
    files
    :param sub_dir: The `sub_dir` parameter in the `download_files` function represents the subdirectory
    within the `work_dir` where the downloaded files will be stored. It is used to specify the relative
    path within the `work_dir` where the files should be saved
    :param files: The `files` parameter is a list of `File` objects that contains information about the
    files to be downloaded. Each `File` object likely has attributes such as `bucket` (the storage
    bucket where the file is located) and `path` (the path to the file within the bucket)
    :type files: List[File]
    """
    storage_client = get_storage_client()
    target_path = os.path.join(work_dir, sub_dir)
    for source in sources:
        file = File(**source)
        file_content = await storage_client.get_file(file.bucket, file.id)
        if file_content:
            filename = os.path.basename(file.id)
            write_storage_files(file_content, target_path, filename)


async def download_module(bucket_name, module_local_path, module_remote_path, version):
    logger = get_run_logger()
    from fa_common.storage import get_storage_client

    storage_client = get_storage_client()
    target_path = os.path.join(module_local_path, version)

    if os.path.exists(target_path):
        logger.info(f"Module version already exists: {module_local_path}/{version}/")
        return

    # @NOTE: the "/" at the tail is quite important
    lst_objs = await storage_client.list_files(bucket_name, f"{module_remote_path}/{version}/")
    lst_files = list(filter(lambda f: not f.dir, lst_objs))

    if len(lst_files) == 0:
        raise ValueError(f"No content was found in the modules remote path: {bucket_name}/{module_remote_path}/{version}")

    ensure_directories_exist([module_local_path, target_path])

    for file in lst_files:
        file_content = await storage_client.get_file(bucket_name, file.id)
        if file_content:
            if ".zip" in file.id:
                extract_zip_from_bytesio(file_content, target_path)
            else:
                filename = os.path.basename(file.id)
                write_storage_files(file_content, target_path, filename)
            logger.info("Module Ready to Use!")
            return
    raise ValueError(f"Module Not Found: {module_remote_path}/{version}")


async def write_params_to_file(input_params, filetype: FileType = FileType.JSON, filename="param.json"):
    """
    Writes the input parameters required for a module in the pre-defined input path.

    Useful for scenarios where the module expects the input_params as input_file rather
    than directly passing the params.

    :param: input_params: dict of parameters
    """
    config = runtime.flow_run.parameters
    if filetype == FileType.JSON:
        with open(os.path.join(os.path.join(config.get("working_dir"), config.get("input_path")), filename), "w") as f:
            json.dump(input_params, f, indent=2)
        return

    if filetype == FileType.TXT:
        raise NotImplementedError("TXT file type handling not implemented.")

    if filetype == FileType.YAML:
        raise NotImplementedError("YAML file type handling not implemented.")

    raise ValueError("Unknown filetype")


async def upload_outputs():
    pass


async def cleanup():
    """
    This function aims to clean up working/temp directories.
    """
    config = runtime.flow_run.parameters
    # temp_directory = tempfile.gettempdir()
    # os.chdir(temp_directory)
    delete_directory(config.get("working_dir"))
    delete_directory(config.get("tmp_dir"))


# ==========================================================================================
####### ####### #     # ######  #          #    ####### #######     #####  ####### #     #
#    #       ##   ## #     # #         # #      #    #          #     # #       ##    #
#    #       # # # # #     # #        #   #     #    #          #       #       # #   #
#    #####   #  #  # ######  #       #     #    #    #####      #  #### #####   #  #  #
#    #       #     # #       #       #######    #    #          #     # #       #   # #
#    #       #     # #       #       #     #    #    #          #     # #       #    ##
#    ####### #     # #       ####### #     #    #    #######     #####  ####### #     #


# ==========================================================================================
class LocalFlowParams(CamelModel):
    standalone_base_path: str
    module_path: str
    module_name: str
    module_bucket: str
    module_remote_path: str
    module_version: str
    module_run_mode: str
    module_run_cmd: str | List[str]
    tmp_dir: str
    input_path: str
    output_path: str
    use_tmp_dir: bool
    ignore_copy_dirs: Optional[List[str]] = []
    working_dir: Optional[str] = None


class LocalWorkflowRun(CamelModel):
    id: WorkflowId = None
    flow_run: WorkflowOutput
    template: WorkflowConfig

    def get_flow_params(self):
        params = {}
        for param in self.template.parameters:
            params[param.name] = param.value
        return LocalFlowParams(**params)

    def get_flow_setup_template(self):
        return {"workflow": self.template.model_dump()}


class LocalTemplateGenerator:
    @classmethod
    def gen_local_workflow(cls, job: JobTemplate, ignore_clean_up: bool = True) -> LocalWorkflowRun:
        base_path = job.template_config.standalone_base_path
        local_path = os.path.join(base_path, job.module.name)
        tmp_dir = tempfile.mkdtemp()
        repo_ref = job.module.version.module_meta.repo_ref

        if isinstance(repo_ref.run_meta.cmd, str):
            repo_ref.run_meta.cmd = [repo_ref.run_meta.cmd]

        if repo_ref.run_meta.mode == ModuleRunModes.VENV:
            if isinstance(repo_ref.run_meta.cmd, list) and len(repo_ref.run_meta.cmd) > 1:
                raise ValueError("When using virtual envs to run a script, only one command line is acceptable.")

            repo_ref.run_meta.cmd[0] = f"{os.path.join(local_path, job.module.version.name)}/{repo_ref.run_meta.cmd[0]}"

        info = LocalFlowParams(
            standalone_base_path=base_path,
            module_path=local_path,
            module_name=job.module.name,
            module_bucket=repo_ref.bucket.name,
            module_remote_path=repo_ref.bucket.base_path,
            module_version=job.module.version.name,
            module_run_mode=repo_ref.run_meta.mode.value,
            module_run_cmd=repo_ref.run_meta.cmd,
            tmp_dir=tmp_dir,
            input_path=repo_ref.run_meta.input_path,
            output_path=repo_ref.run_meta.output_path,
            use_tmp_dir=repo_ref.use_tmp_dir,
            ignore_copy_dirs=repo_ref.ignore_copy,
        )

        input_params = job.inputs.parameters
        if isinstance(input_params, str):
            # If it is string then it should be a JSON_STR
            input_params = json.loads(input_params)

        if not isinstance(input_params, dict):
            raise ValueError("Input Parameters should be convertable to python dictionary.")

        base = cls.gen_base_block(info, runner="sequential")
        task_get_module = cls.gen_download_module()
        task_work_dir = cls.gen_working_directory(info)
        task_clean_up = cls.gen_flow_cleanup()

        base.get("workflow").get("tasks").append(task_get_module)
        base.get("workflow").get("tasks").append(task_work_dir)
        if len(job.inputs.files) > 0:
            # downloads = [file.id for file in job.inputs.files ]
            task_download = cls.gen_download_temp(job.inputs.files)
            base.get("workflow").get("tasks").append(task_download)

        if info.module_run_mode == ModuleRunModes.SUBPROCESS or info.module_run_mode == ModuleRunModes.VENV:
            task_write_params = cls.gen_write_param_files(input_params)
            base.get("workflow").get("tasks").append(task_write_params)

            task_run = cls.gen_run_module_subprocess(info)
        else:
            task_run = cls.gen_run_module_func(info, input_params)

        base.get("workflow").get("tasks").append(task_run)

        if not ignore_clean_up:
            base.get("workflow").get("tasks").append(task_clean_up)

        with open(os.path.join(tmp_dir, "setup.yaml"), "w") as file:
            yaml.safe_dump(base, file, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return LocalWorkflowRun(**base.get("workflow"))

    @classmethod
    def gen_base_block(cls, info: LocalFlowParams, runner="sequential"):
        flow_params = [{"name": k, "value": v} for k, v in info.model_dump().items()]
        return {"workflow": {"name": info.module_name, "runner": runner, "parameters": flow_params, "tasks": []}}

    @classmethod
    def gen_download_module(cls):
        return {
            "name": "pull-module-version",
            "plugin_path": dirname,  # os.path.join(config_module.get("STANDALONE_BASE_PATH"), "plugins"),
            "module": "local_utils",
            "task": "download_module",
            "inputs": {
                "parameters": [
                    {"name": "bucket_name", "value": "module_bucket", "type": "flow"},
                    {"name": "module_local_path", "value": "module_path", "type": "flow"},
                    {"name": "module_remote_path", "value": "module_remote_path", "type": "flow"},
                    {"name": "version", "value": "module_version", "type": "flow"},
                ]
            },
        }

    @classmethod
    def gen_working_directory(cls, info):
        return {
            "name": "generate-working directory",
            "plugin_path": dirname,  # os.path.join(config_module.get("STANDALONE_BASE_PATH"), "plugins"),
            "module": "local_utils",
            "task": "init_working_directory",
            "inputs": {"parameters": [{"name": "ignore_dirs", "value": info.ignore_copy_dirs}]},
        }

    @classmethod
    def gen_download_temp(cls, files: List[File]):
        sources = []
        for file in files:
            sources.append(file.model_dump())

        return {
            "name": "download-required-files",
            "plugin_path": dirname,  # os.path.join(config_module.get("STANDALONE_BASE_PATH"), "plugins"),
            "module": "local_utils",
            "task": "download_files",
            "inputs": {
                "parameters": [
                    # {"name": "bucket_name", "value": settings.BUCKET_NAME},
                    {"name": "work_dir", "value": "working_dir", "type": "flow"},
                    {"name": "sub_dir", "value": "input_path", "type": "flow"},
                    {"name": "sources", "value": sources},
                ]
            },
        }

    @classmethod
    def gen_write_param_files(cls, input_params):
        return {
            "name": "write-param-json",
            "plugin_path": dirname,  # os.path.join(config_module.get("STANDALONE_BASE_PATH"), "plugins"),
            "module": "local_utils",
            "task": "write_params_to_file",
            "inputs": {
                "parameters": [
                    {"name": "input_params", "value": input_params},
                    {"name": "filetype", "value": "json"},
                    {"name": "filename", "value": "param.json"},
                ]
            },
        }

    @classmethod
    def gen_run_module_func(cls, info, input_params):
        """
        Running an module function provides convenience, but the restriction is
        you should use the base environment that is set for your app/api.
        """
        plugin_path = info.get("tmp_dir") if info.use_tmp_dir else f"{info.module_path}/{info.module_version}"
        return {
            "name": "run-module-func",
            "plugin_path": plugin_path,
            "module": "main",
            "task": "main",
            "inputs": {"parameters": [{"name": "input_params", "value": input_params}]},
        }

    @classmethod
    def gen_run_module_subprocess(cls, info):
        """
        Use this to run:
        - Executables
        - Python modules that have isolated environments
        """
        return {
            "name": "run-module-exe",
            "module": "logic.actions",
            "task": "run_standalone_script_modified",
            "inputs": {
                "parameters": [
                    {"name": "base_path", "value": info.tmp_dir},
                    {"name": "package_name", "value": ""},
                    {"name": "package_run_cmds", "value": info.module_run_cmd},
                ]
            },
        }

    @classmethod
    def gen_flow_cleanup(cls):
        return {"name": "clean-up", "plugin_path": dirname, "module": "local_utils", "task": "cleanup"}
