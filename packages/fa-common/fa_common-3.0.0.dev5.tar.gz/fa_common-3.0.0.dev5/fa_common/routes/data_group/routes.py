# from typing import List, Optional

# import gcsfs
# import pandas

# from fastapi import APIRouter, Depends
# from fastapi import File as FAFile
# from fastapi import Path, UploadFile
# from pandas.core.frame import DataFrame
# from pandas.errors import ParserError
# from starlette.responses import StreamingResponse

# from fa_common import NotFoundError, get_settings
# from fa_common.storage import File as FileRef
# from fa_common.storage.utils import get_storage_client
# from fa_common.routes.shared import Message
# from fa_common.routes.users import User, get_current_user

# from . import service
# from .models import DatasetSZ, DatasetSZPost, DatasetType, PreviewRow


# DATASET_NAME_REGEX = r"^[0-9a-zA-Z_\. ]+$"


# router = APIRouter()

# @router.get("/preview")
# async def preview_dataset(gsUri: str) -> List[PreviewRow]:
#     # Try to read the file with separator None and engine python
#     # so that pandas will try to automatically detact the delimiter.
#     # This may not always work, auto detection sometimes fail when tried with spaces.
#     # Hence if there is a perse error, we try again with spaces,
#     # if that one fails too, the endpoint will throw error.
#     try:
#         reader: DataFrame = pandas.read_csv(gsUri, sep=None, header=None, chunksize=5, engine="python")
#         return service.construct_preview(reader)
#     except ParserError:
#         reader = pandas.read_csv(gsUri, sep=r"\s+", header=None, chunksize=5)
#         return service.construct_preview(reader)


# @router.get("/process/dfn")
# async def process_dfn(datUri: str, dfnUri: str, current_user: User = Depends(get_current_user)) -> any:
#     settings = get_settings()
#     data = await service.load_data({"fdat": datUri, "fdfn": dfnUri}, current_user, settings)
#     container = data["container"]

#     # json would convert very low values (^-15) into 0.
#     # We cannot get around that with json as the highest value permitted for double precision is 15.
#     # Setting orient records would set rows as column: value object format,
#     # which is easier to identify and handle.
#     columns = container["data"].columns.tolist()
#     values = container["data"].head().to_json(double_precision=15, orient="records")
#     return {"headers": columns, "values": values, "tempFileUri": data["tempFileUri"]}


# @router.get("", response_model=List[DatasetSZ.response_model])  # type: ignore
# async def list_datasets(
#     include_public: bool = True,
#     preview: bool = False,
#     dataset_type: Optional[DatasetType] = None,
#     current_user: User = Depends(get_current_user),
# ) -> List[str]:
#     """List Users Datasets"""
#     datasets = await service.get_datasets_for_user(current_user, include_public, dataset_type)
#     return [ds.dict(exclude=({"preview"} if not preview else {})) for ds in datasets]


# @router.post("", response_model=DatasetSZPost.response_model)
# async def create_dataset(
#     dataset: DatasetSZPost,
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Create dataset record
#     """

#     dataset = await service.create_dataset(current_user, dataset.dict(), dataset.file_ref)

#     return dataset.dict()


# @router.get("/tempfile", response_model=List[FileRef])  # type: ignore
# async def list_temporary_files(
#     current_user: User = Depends(get_current_user),
# ) -> List[str]:
#     """List Users Temporay Files that can be used to create a dataset"""
#     settings = get_settings()
#     storage_client = get_storage_client()
#     return await storage_client.list_files(current_user.bucket_id, f"{settings.DATASET_FOLDER}/TEMP")


# @router.delete("/tempfile", response_model=Message)  # type: ignore
# async def delete_all_temporary_files(
#     current_user: User = Depends(get_current_user),
# ) -> List[str]:
#     """Delete all Temporary Files"""
#     storage_client = get_storage_client()
#     settings = get_settings()

#     await storage_client.delete_file(
#         current_user.bucket_id, f"{settings.DATASET_FOLDER}/TEMP/", recursive=True
#     )

#     return Message(message="Deleted all temporary files.")


# @router.delete(
#     "/tempfile/{file_name}",
#     response_model=Message,
#     responses={404: {"description": "File Not Found"}},
# )  # type: ignore
# async def delete_temporary_file(
#     file_name: str,
#     current_user: User = Depends(get_current_user),
# ) -> List[str]:
#     """Delete a Temporary File"""
#     storage_client = get_storage_client()
#     settings = get_settings()
#     if not storage_client.file_exists(
#         current_user.bucket_id, f"{settings.DATASET_FOLDER}/TEMP/{file_name}"
#     ):
#         return NotFoundError(f"Temporary File with the name {file_name} not found.")

#     await storage_client.delete_file(
#         current_user.bucket_id, f"{settings.DATASET_FOLDER}/TEMP/{file_name}"
#     )

#     return Message(message=f"Deleted temporary file {file_name}.")


# @router.get(
#     "/{dataset_name}/file",
#     response_class=StreamingResponse,
#     responses={404: {"description": "File Not Found"}},
# )  # type: ignore
# async def download_dataset_file(
#     dataset_name: str = Path(..., regex=DATASET_NAME_REGEX),
#     current_user: User = Depends(get_current_user),
# ):
#     """Downloads a file associated w ith a dataset"""
#     dataset = await service.get_dataset(current_user.id, dataset_name, expected=True)
#     settings = get_settings()
#     if dataset.file_ref is None:
#         raise NotFoundError(f"Dataset {dataset_name} does not have a file associated with it.")

#     try:
#         fs = gcsfs.GCSFileSystem(project=settings.CLOUD_PROJECT)
#         file_path = dataset.file_ref.gs_uri.replace("gs://", "")
#         assert fs.exists(file_path)
#     except AssertionError as err:
#         raise NotFoundError(
#             f"Dataset {dataset_name} has a file {dataset.file_ref.gs_uri} "
#             + "but it can't be found in the bucket."
#         ) from err

#     file = fs.open(file_path, "rb")
#     return StreamingResponse(
#         file,
#         media_type=dataset.file_ref.content_type,
#         headers={"Content-Disposition": f"attachment;filename={dataset.file_ref.name}"},
#     )


# @router.get("/{dataset_name}", response_model=DatasetSZ.response_model)  # type: ignore
# async def get_dataset(
#     dataset_name: str = Path(..., regex=DATASET_NAME_REGEX),
#     current_user: User = Depends(get_current_user),
# ) -> List[str]:
#     """Gets a dataset given the dataset name"""
#     dataset = await service.get_dataset(current_user.id, dataset_name)

#     return dataset.dict()


# @router.delete("/{name}", response_model=Message)
# async def delete_dataset(
#     name: str = Path(..., regex=DATASET_NAME_REGEX),
#     current_user: User = Depends(get_current_user),
# ) -> Message:
#     """Deletes a dataset given the dataset name"""

#     delete_outcome = await service.delete(current_user, name)

#     if not delete_outcome:
#         raise NotFoundError(f"Dataset {name} not found")

#     return Message(message=f"Deleted dataset {name}.")


# @router.post("/upload", response_model=FileRef)
# async def upload_file(
#     file_data: UploadFile = FAFile(...),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Upload a file for a dataset
#     """
#     settings = get_settings()
#     file_ref = await service.upload_file(current_user, file_data, settings)

#     return file_ref
