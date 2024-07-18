# from io import BytesIO
# from typing import List, Optional

# import gcsfs
# import pandas
# import regex
# from fa_common.exceptions import NotFoundError
# from fa_common import get_settings
# from fa_common import logger as LOG
# from fa_common.db import Operator, WhereCondition
# from fa_common.exceptions import AlreadyExistsError, BadRequestError, StorageError
# from fa_common.storage import File, get_storage_client
# from fastapi import UploadFile
# from pandas.core.frame import DataFrame
# from pydantic import BaseSettings

# from fa_common.routes.users import User

# from .models import CSVConfig, Dataset, DatasetType, PreviewRow

# data_types = {"i": "int64", "f": "float64", "e": "float64", "a": "str"}


# async def load_data(handle, user: User, settings: BaseSettings):
#     data_container = dict()

#     data_container["fdat"] = handle["fdat"]
#     data_container["fdfn"] = handle["fdfn"]

#     if data_container["fdat"].endswith(".csv"):
#         data_container["dfn"] = read_header(data_container, settings)
#         handle["import_method"] = "csv"
#         handle["skip_lines"] = 1
#         handle["csv_sep"] = ","
#         handle["csv_head"] = 0
#     elif data_container["fdfn"].endswith(".hdr"):
#         data_container["dfn"] = read_hdr(data_container, settings)
#         handle["import_method"] = "csv"
#         handle["csv_sep"] = r"\s+"
#         handle["csv_head"] = None
#     elif data_container["fdat"].endswith(".dat") and data_container["fdfn"]:
#         handle["import_method"] = "fwf"
#         data_container["dfn"] = read_dfn(data_container, handle, settings)
#     else:
#         raise ValueError("Input data file not supported. Must be .asc, .dat or .csv")

#     data_container["data"] = import_dat(data_container, handle)
#     client = get_storage_client()

#     # Extract filename from gsuri to use as the temp file name
#     temp_file_name = handle["fdat"].rsplit("/", 1)[1].rsplit(",", 1)[0]

#     file_ref = await client.upload_string(
#         data_container["data"].to_json(double_precision=15, orient="records"),
#         user.bucket_id,
#         f"{settings.DATASET_FOLDER}/TEMP/{temp_file_name}.json",
#         "application/json",
#     )

#     return {"container": data_container, "tempFileUri": file_ref.gs_uri}


# def read_header(data_container, settings: BaseSettings):
#     fs = gcsfs.GCSFileSystem(project=settings.CLOUD_PROJECT)

#     with fs.open(data_container["fdat"].replace("gs://", "")) as f:
#         header_row = list(map(lambda x: x.decode("utf-8"), f.readlines()))[0]

#     repcode = {}
#     chans = header_row.split(",")
#     # Initialise column name and name as empty strings.
#     # We will use them to capture annotation ([]) cases.
#     # They will also be used to verify if any annotation is found.
#     columnName = ""
#     name = ""
#     for chan in chans:
#         chan = chan.rstrip()
#         if "[" in chan:
#             # Found a [ annotation, hence set the name to it.
#             name = chan.split("[")[0]
#         else:
#             name = ""
#         if columnName == "":
#             if name == "":
#                 # No annotation exists, hence set the column name normally.
#                 repcode[chan] = {}
#                 repcode[chan]["col"] = chan
#                 repcode[chan]["elems"] = 1
#             else:
#                 # If there is a name, set column name to keep a record of it.
#                 columnName = name
#         else:
#             if columnName == name:
#                 # If column name and name are same, do nothing until the end of array.
#                 continue
#             else:
#                 # Reached the end of current array, so set column with the last array.
#                 arrayChan = chans[chans.index(chan) - 1].split("[")
#                 arrayChanName = arrayChan[0]
#                 arrayChanElements = arrayChan[1].split("]")[0]
#                 repcode[arrayChanName] = {}
#                 repcode[arrayChanName]["col"] = arrayChanName
#                 repcode[arrayChanName]["elems"] = int(arrayChanElements)

#                 if name == "":
#                     # After reaching end of array, we found a normal column, so process accordingly.
#                     columnName = ""
#                     repcode[chan] = {}
#                     repcode[chan]["col"] = chan
#                     repcode[chan]["elems"] = 1
#                 else:
#                     # After reaching the end of array, we found another array.
#                     # Set it to column name to process this array.
#                     columnName = name

#     return repcode


# def read_hdr(data_container, settings: BaseSettings):
#     repcode = {}
#     fs = gcsfs.GCSFileSystem(project=settings.CLOUD_PROJECT)

#     with fs.open(data_container["fdfn"].replace("gs://", "")) as f:
#         fdfn_content = list(map(lambda x: x.decode("utf-8"), f.readlines()))
#     elems_tot = 0
#     ccol = 1
#     for line in fdfn_content:
#         marray = regex.match(r"\s*(\d+)\s*\-\s*(\d+)\s+(.*?)\s*\n", line)
#         msingle = regex.match(r"\s*(\d+)\s+(.*?)\s*\n", line)
#         ocol = int(ccol) + elems_tot
#         if marray:
#             chan = marray.group(3)
#             repcode[chan] = {}
#             repcode[chan]["col"] = ocol
#             nelems = int(float(marray.group(2)) - float(marray.group(1)) + 1)
#             repcode[chan]["elems"] = nelems
#             elems_tot = elems_tot + nelems - 1
#         if msingle:
#             chan = msingle.group(2)
#             repcode[chan] = {}
#             repcode[chan]["col"] = ocol
#             repcode[chan]["elems"] = 1
#         ccol = ccol + 1

#     return repcode


# def read_dfn(data_container, handle, settings: BaseSettings):
#     fs = gcsfs.GCSFileSystem(project=settings.CLOUD_PROJECT)

#     with fs.open(data_container["fdfn"].replace("gs://", "")) as f:
#         fdfn_content = list(map(lambda x: x.decode("utf-8"), f.readlines()))

#     dfn_expand = False
#     if "dfn_expand" in handle:
#         if handle["dfn_expand"]:
#             dfn_expand = True
#     repcode = {}
#     elems_tot = 0

#     coladd = -1
#     for line in fdfn_content[:]:
#         parts = regex.split(",|;|:", line)
#         if regex.match("END DEFN", parts[2]):
#             break
#         col = regex.search(r"\d+", parts[0])
#         if col:
#             ccol = col.group(0)
#             if coladd == -1:
#                 if int(ccol) == 1:
#                     coladd = 0
#                 elif int(ccol) == 0:
#                     coladd = 1
#             if regex.match("RT=(.+)", parts[1]):
#                 # special case where row is prefixed by string i.e. DATA
#                 m = regex.match(r"(\w+)(\d+)", parts[3])
#                 repcode["__ignore__"] = {}
#                 repcode["__ignore__"]["col"] = int(ccol) + elems_tot + coladd
#                 repcode["__ignore__"]["len"] = int(m.group(2))
#                 repcode["__ignore__"]["dtype"] = data_types[m.group(1).lower()]
#                 repcode["__ignore__"]["elems"] = 1
#                 coladd = coladd + 1
#                 del parts[2]
#                 del parts[2]
#             elements = regex.search(r"(\d*)(\w)(\d+)", parts[3])
#             nelems = elements.group(1)
#             dtype = elements.group(2)
#             length = int(elements.group(3))
#             ocol = int(ccol) + elems_tot + coladd
#             chan = parts[2].strip()
#             if nelems:
#                 if dfn_expand:
#                     for i in range(int(nelems)):
#                         elemchan = chan + "_" + str(i)
#                         repcode[elemchan] = {}
#                         repcode[elemchan]["col"] = int(ccol) + i
#                         repcode[elemchan]["elems"] = 1
#                         repcode[elemchan]["dtype"] = data_types[dtype.lower()]
#                         repcode[elemchan]["len"] = length
#                         repcode[elemchan]["fmt"] = parts[3]
#                 else:
#                     repcode[chan] = {}
#                     repcode[chan]["col"] = ocol
#                     nelems = int(nelems)
#                     elems_tot = elems_tot + nelems - 1
#                     repcode[chan]["elems"] = nelems
#                     repcode[chan]["ndtype"] = data_types[dtype.lower()]
#                     repcode[chan]["len"] = length * nelems
#                     repcode[chan]["nlen"] = length
#                     repcode[chan]["nfmt"] = parts[3]
#             else:
#                 repcode[chan] = {}
#                 repcode[chan]["col"] = ocol
#                 repcode[chan]["elems"] = 1
#                 repcode[chan]["dtype"] = data_types[dtype.lower()]
#                 repcode[chan]["len"] = length
#                 repcode[chan]["fmt"] = parts[3]

#     return repcode


# def import_dat(data_container, handle):
#     def conv2array(self):
#         array = tuple(float(x) for x in regex.split(r"\s+", self.strip()))
#         return array

#     if handle["import_method"] == "csv":
#         temp = pandas.read_csv(data_container["fdat"], header=handle["csv_head"], sep=handle["csv_sep"])
#         data = pandas.DataFrame()
#         i = 0
#         for col in data_container["dfn"].keys():
#             if data_container["dfn"][col]["elems"] > 1:
#                 elems = data_container["dfn"][col]["elems"]
#                 data[col] = [temp.iloc[row].iloc[i : i + elems].to_numpy() for row in temp.index.values]
#                 i = i + data_container["dfn"][col]["elems"]
#             else:
#                 data[col] = temp[temp.columns[i]]
#                 i = i + 1
#             if "dtype" in data_container["dfn"][col].values():
#                 data[col].astype(data_container["dfn"][col]["dtype"])
#     elif handle["import_method"] == "fwf":
#         fdat = data_container["fdat"]
#         fdfn = data_container["dfn"]
#         data = pandas.read_fwf(
#             fdat,
#             names=fdfn.keys(),
#             widths=[fdfn[x]["len"] for x in fdfn.keys()],
#             converters={x: conv2array for x in fdfn.keys() if fdfn[x]["elems"] > 1},
#             dtype={x: fdfn[x]["dtype"] for x in fdfn.keys() if "dtype" in fdfn[x].values()},
#         )
#     else:
#         raise ValueError("Input data file not supported. Must be .asc, .dat or .csv")

#     # delete ignore channel
#     if "__ignore__" in data.columns:
#         data = data.drop(["__ignore__"], axis=1)
#     return data


# async def get_dataset(user_id: str, name: str, expected: bool = True):
#     """[summary]

#     Arguments:
#         user_id {str} -- [description]
#         name {str} -- [description]

#     Keyword Arguments:
#         expected {bool} -- [description] (default: {True})

#     Raises:
#         NotFoundError: When dataset is expected but does not exist
#     """
#     conditions = [
#         WhereCondition(field="user_id", operator=Operator.EQUALS, value=user_id),
#         WhereCondition(field="name", operator=Operator.EQUALS, value=name),
#     ]
#     dataset = await Dataset.find_one(where=conditions)
#     if expected and dataset is None:
#         LOG.warning(f"Dataset for user: {user_id} with name: {name} does not exist but was expected")
#         raise NotFoundError(f"Dataset: {name} does not exist")
#     return dataset


# async def create_dataset(user: User, dataset: dict, settings: BaseSettings, file_ref_in: File = None) -> Dataset:
#     dataset = Dataset(**dataset)
#     name = dataset.name
#     LOG.info(f"Dataset {dataset.name}")

#     existing = await get_dataset(user.id, name, expected=False)

#     if existing is not None:
#         raise AlreadyExistsError(f"Dataset for user: {user.id} with name: {name} already exists", ["name"])
#     elif file_ref_in is None:
#         raise BadRequestError("Fileref is empty")
#     else:
#         file_ref = file_ref_in

#         if file_ref is not None and file_ref.path is not None and len(file_ref.path) > 0:
#             client = get_storage_client()
#             try:
#                 file_ref = await client.rename_file(
#                     user.bucket_id,
#                     f"{file_ref.path}/{file_ref.name}",
#                     f"{settings.DATASET_FOLDER}/{dataset.name}/{file_ref.name}",
#                 )
#             except StorageError as err:
#                 raise NotFoundError(f"The referenced file does not exist: {str(err)}") from err

#         dataset.file_ref = file_ref
#         if dataset.csv_config is not None:
#             dataset.preview = await peek_file(user, file_ref, dataset.csv_config)

#         dataset.init(user.id)

#         await dataset.save()

#         return dataset


# async def delete(user: User, name: str) -> bool:
#     """Deletes the dataset

#     Arguments:
#         user_token {[str]} -- [user]
#         name {[str]} -- [dataset]

#     Returns:
#         [bool] -- [True if a file was deleted false if it didn't exist]
#     """
#     dataset = await get_dataset(user.id, name, expected=False)

#     if dataset is not None:

#         if len(dataset.project_links) == 0:
#             await Dataset.delete(dataset.id)
#             return True
#         else:
#             LOG.warning(
#                 f"Dataset for user: {user.id} with name: {name} has {len(dataset.project_links)} "
#                 + "project links and is unable to be deleted"
#             )
#             raise ValueError(
#                 f"Dataset: {name} has {len(dataset.project_links)} project links and is unable "
#                 + "to be deleted"
#             )

#     return False


# async def upload_file(user: User, data: UploadFile, settings: BaseSettings) -> File:
#     client = get_storage_client()
#     # Setting timeout to 600 to stop large file uploads from timing out.
#     file_ref = await client.upload_file(data, user.bucket_id, f"{settings.DATASET_FOLDER}/TEMP", 600)

#     return file_ref


# async def list_files(user: User, settings: BaseSettings) -> List[File]:
#     """[summary]

#     Keyword Arguments:
#         test_path {str} -- [description] (default: {"test_data"})

#     Returns:
#         [type] -- [description]
#     """

#     storage_client = get_storage_client()
#     files = await storage_client.list_files(user.bucket_id, settings.DATASET_FOLDER)
#     datasets = []
#     for file in files:
#         LOG.debug("List user data blob: {}".format(file))
#         datasets.append(file)
#     return datasets


# async def get_file_ref(user: User, file_name: str, settings: BaseSettings) -> File:
#     """[summary]

#     Keyword Arguments:
#         test_path {str} -- [description] (default: {"test_data"})

#     Returns:
#         [type] -- [description]
#     """
#     storage_client = get_storage_client()

#     file_ref: File = await storage_client.get_file_ref(
#         user.bucket_id, f"{settings.DATASET_FOLDER}/{file_name}"
#     )
#     assert (
#         file_ref is not None
#     ), f"There is no file {settings.DATASET_FOLDER}/{file_name} uploaded to the bucket"

#     return file_ref


# async def get_file(user: User, file_name: str, settings: BaseSettings) -> Optional[BytesIO]:
#     """[summary]

#     Keyword Arguments:
#         test_path {str} -- [description] (default: {"test_data"})

#     Returns:
#         [type] -- [description]
#     """
#     storage_client = get_storage_client()

#     return await storage_client.get_file(user.bucket_id, f"{settings.DATASET_FOLDER}/{file_name}")


# async def get_file_path(user: User, file_name: str) -> str:
#     """[summary]

#     Keyword Arguments:
#         test_path {str} -- [description] (default: {"test_data"})

#     Returns:
#         [type] -- [description]
#     """
#     settings = get_settings()
#     file_ref = await get_file_ref(user, file_name, settings)

#     return "gs://" + file_ref.id.rsplit("/", 1)[0]


# def construct_preview(reader: DataFrame) -> List[PreviewRow]:
#     chunk = reader.get_chunk()
#     array = chunk.values.tolist()

#     preview = []
#     for i in array:
#         preview.append(PreviewRow(row=i))

#     return preview


# async def peek_file(user: User, file_ref: File, csvConfig: CSVConfig) -> List[PreviewRow]:
#     """[summary]

#     Keyword Arguments:
#         test_path {str} -- [description] (default: {"test_data"})

#     Returns:
#         [type] -- [description]
#     """
#     # separator of w means whitespace
#     separator = r"\s+" if csvConfig.separator == "w" else csvConfig.separator
#     header = None if not csvConfig.header_line else 0

#     # read first 5 lines and put into list of lists
#     reader = pandas.read_csv(file_ref.gs_uri, sep=separator, header=header, chunksize=5)
#     chunk = reader.get_chunk()

#     array = chunk.values.tolist()

#     preview = []
#     for i in array:
#         preview.append(PreviewRow(row=i))

#     return preview


# async def get_datasets_for_user(
#     user: User, include_public=True, type: DatasetType = None
# ) -> List[Dataset]:
#     """[summary]

#     Arguments:
#         user_token {str} -- [description]

#     Returns:
#         [type] -- [description]
#     """

#     conditions = [WhereCondition(field="user_id", operator=Operator.EQUALS, value=user.id)]
#     if type is not None:
#         conditions.append(WhereCondition(field="type", operator=Operator.EQUALS, value=type))

#     datasets = await Dataset.list(where=conditions)

#     if include_public:
#         public_cond = [WhereCondition(field="public", operator=Operator.EQUALS, value=True)]
#         if type is not None:
#             public_cond.append(WhereCondition(field="type", operator=Operator.EQUALS, value=type))
#         datasets.extend(await Dataset.list(where=public_cond))

#     return datasets


# async def get_dataset_for_user(user: User, dataset_id: str) -> Dataset:
#     """[summary]

#     Arguments:
#         user_token {str} -- [description]

#     Returns:
#         [type] -- [description]
#     """
#     datasets = await Dataset.list(
#         where=[
#             WhereCondition(field="user_id", operator=Operator.EQUALS, value=user.id),
#             WhereCondition(field="dataset_id", operator=Operator.EQUALS, value=dataset_id),
#         ]
#     )

#     if datasets is None or len(datasets) < 1:
#         raise NotFoundError(f"Dataset {dataset_id} could not be found")
#     elif len(datasets) > 1:
#         raise RuntimeError(f"Multiple datasets found with id: {dataset_id} for user {user.id}")

#     return datasets[0]


# async def delete_datasets_for_user(user: User) -> bool:
#     """[summary]

#     Arguments:
#         user_token {str} -- [description]

#     Returns:
#         [type] -- [description]
#     """
#     datasets = await get_datasets_for_user(user)

#     if len(datasets) > 0:
#         for dataset in datasets:
#             await Dataset.delete(dataset.id)

#     return True
