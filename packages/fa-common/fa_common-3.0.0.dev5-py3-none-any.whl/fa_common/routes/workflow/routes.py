## TODO: Need to revisit these routes in the context of the recent work with Argo and what is required for XT Workbench
## FYI what is currently here is copied over from GPT
## @Ben to advise of possible routes that are possible/needed

# from typing import List

# from fastapi import APIRouter, Depends, Path, Response
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import StreamingResponse, UJSONResponse

# import gcsfs

# from fa_common.exceptions import NotFoundError
# from fa_common import logger as LOG
# from fa_common import get_settings
# from fa_common.storage import File
# from fa_common.workflow import JobAction, JobRun, WorkflowRun
# from fa_common.workflow import delete_workflow as delete_work
# from fa_common.workflow import get_job_file, get_job_file_refs, get_job_log, get_job_output
# from fa_common.workflow import get_workflow as get_work, get_job_run
# from fa_common.workflow import job_action
# from fa_common.routes.shared import Message
# # from fa_common import logger as LOG
# from fa_common.routes.users import User, get_current_user


# router = APIRouter()

# @router.get("/job/{job_id}", response_model=JobRun)
# async def get_job(
#     job_id: int = Path(..., title="Job Run ID"),
#     current_user: User = Depends(get_current_user),
#     include_log: bool = False,
#     include_output: bool = True,
# ):
#     """Get job summary including output if available"""

#     try:
#         assert current_user.id is not None
#         job_run = await get_job_run(
#             current_user.id,
#             current_user.bucket_id,
#             job_id,
#             include_log,
#             include_output,
#             True,
#         )
#     except ValueError as err:
#         LOG.warning(err)
#         raise NotFoundError(f"Job with id {job_id} could not be found.") from err

#     return job_run


# @router.get("/job/{job_id}/log")
# async def get_log(
#     job_id: int = Path(..., title="Job Run ID"),
#     current_user: User = Depends(get_current_user),
# ):
#     try:
#         assert current_user.id is not None
#         log = await get_job_log(current_user.id, job_id)
#         return Response(content=log, media_type="text/plain")
#     except ValueError as err:
#         LOG.warning(err)
#         raise NotFoundError(f"Job with id {job_id} could not be found.") from err


# @router.get("/workflow/{workflow_id}/job/{job_id}/output")
# async def get_output(
#     workflow_id: int = Path(..., title="Workflow Run ID"),
#     job_id: int = Path(..., title="Job Run ID"),
#     current_user: User = Depends(get_current_user),
# ):
#     """Gets the output directly from the bucket
#     return raw output as json
#     """
#     return UJSONResponse(
#         content=jsonable_encoder(await get_job_output(current_user.bucket_id, workflow_id, job_id))
#     )


# @router.get("/workflow/{workflow_id}/job/{job_id}/file", response_model=List[File])
# async def list_files(
#     workflow_id: int = Path(..., title="Workflow Run ID"),
#     job_id: int = Path(..., title="Job Run ID"),
#     current_user: User = Depends(get_current_user),
# ):
#     """Gets a list of all the files uploaded for a job"""
#     return await get_job_file_refs(current_user.bucket_id, workflow_id, job_id)


# @router.get("/workflow/{workflow_id}/job/{job_id}/file/{filename}")
# async def get_file(
#     workflow_id: int = Path(..., title="Workflow Run ID"),
#     job_id: int = Path(..., title="Job Run ID"),
#     filename: str = Path(..., title="Filename"),
#     current_user: User = Depends(get_current_user),
# ):
#     """Gets a list of all the files uploaded for a job"""
#     file_ref = await get_job_file(current_user.bucket_id, workflow_id, job_id, filename, ref_only=True)
#     if file_ref is None:
#         raise NotFoundError(f"File {filename} not found.")
#     assert isinstance(file_ref, File)
#     settings = get_settings()
#     fs = gcsfs.GCSFileSystem(project=settings.CLOUD_PROJECT)
#     file = fs.open(file_ref.gs_uri.replace("gs://", ""), "rb")

#     return StreamingResponse(
#         file,
#         media_type=file_ref.content_type,
#         headers={"Content-Disposition": f"attachment;filename={filename}"},
#     )


# @router.delete("/job/{job_id}", response_model=Message)
# async def delete_job(
#     job_id: int = Path(..., title="Job Run ID"),
#     current_user: User = Depends(get_current_user),
# ):
#     try:
#         assert current_user.id is not None
#         await job_action(current_user.id, job_id, JobAction.DELETE)
#         return Message(message=f"Job {job_id} deleted successfully.")
#     except ValueError as err:
#         LOG.warning(err)
#         raise NotFoundError(f"Job with id {job_id} could not be found.") from err


# @router.post("/job/{job_id}/{action}", response_model=JobRun, responses={202: {"model": Message}})
# async def run_job_action(
#     job_id: int = Path(..., title="Job Run ID"),
#     action: JobAction = Path(..., title="Job Action"),
#     current_user: User = Depends(get_current_user),
# ):
#     try:
#         assert current_user.id is not None
#         job = await job_action(current_user.id, job_id, action)
#         if action is JobAction.DELETE:
#             return UJSONResponse(
#                 status_code=202,
#                 content={"message": f"Job {job_id} deleted successfully."},
#             )
#         return job
#     except ValueError as err:
#         LOG.warning(err)
#         raise NotFoundError(f"Job with id {job_id} could not be found.") from err


# @router.get("/workflow/{workflow_id}", response_model=WorkflowRun)
# async def get_workflow(
#     workflow_id: int = Path(..., title="Workflow Run ID"),
#     include_ouput: bool = False,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get job summary including output if available"""

#     try:
#         assert current_user.id is not None
#         work_run = await get_work(
#             current_user.id,
#             current_user.bucket_id,
#             workflow_id,
#             include_ouput,
#             file_refs=True,
#         )
#     except ValueError as err:
#         LOG.warning(err)
#         raise NotFoundError(f"Workflow with id {workflow_id} could not be found.") from err

#     return work_run


# @router.delete("/workflow/{workflow_id}", response_model=Message)
# async def delete_workflow(
#     workflow_id: int = Path(..., title="Workflow Run ID"),
#     current_user: User = Depends(get_current_user),
# ):
#     """Delete workflow"""

#     try:
#         assert current_user.id is not None
#         await delete_work(current_user.id, current_user.bucket_id, workflow_id)
#         return Message(message=f"Workflow {workflow_id} deleted successfully.")
#     except ValueError as err:
#         LOG.warning(err)
#         raise NotFoundError(f"Workflow with id {workflow_id} could not be found.") from err
