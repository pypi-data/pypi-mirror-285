# from enum import Enum
# from typing import List, Optional

# from pydantic import Field

# from fa_common.db import DocumentDBModel
# from fa_common.serializers import CamelModel, Serializer, patch
# from fa_common.storage import File
# from fa_common import get_settings


# class PreviewRow(CamelModel):
#     row: List[str]


# class CSVConfig(CamelModel):
#     filename: str
#     header_line: bool
#     separator: str


# class DataFormat(str, Enum):
#     none = None
#     CSV = "CSV"
#     NETCDF = "NetCDF"
#     SQL = "SQL"
#     JSON = "JSON"
#     GEO_TIFF = "GEO_TIFF"


# # TODO: Implement this properly at the moment it's here as an example
# class DatasetType(str, Enum):
#     none = None
#     AEM_INPUT = "AEMData"
#     SENSI_RESULTS = "SENSIResults"
#     AEM_INVERSION = "AEMInversion"
#     TOTAL_MAGNETIC_INTENSITY = "TotalMagneticIntensity"


# class Dataset(DocumentDBModel):
#     user_id: str = ""
#     name: str = Field(..., regex=r"^$|^[0-9a-zA-Z_\. ]+$")
#     public: bool = False
#     project_links: List[str] = []
#     data_format: Optional[DataFormat] = DataFormat.none
#     type: Optional[DatasetType] = DatasetType.none
#     file_ref: Optional[File]
#     csv_config: Optional[CSVConfig]
#     preview: Optional[List[PreviewRow]] = []

#     # TODO Add spatial metadata

#     @classmethod
#     def get_db_collection(cls) -> str:
#         return f"{get_settings().COLLECTION_PREFIX}datasets"

#     def link_project(self, project_id: str):
#         if project_id not in self.project_links:
#             self.project_links.append(project_id)

#     def unlink_project(self, project_id: str):
#         if project_id in self.project_links:
#             self.project_links.remove(project_id)

#     def init(self, user_id: str) -> None:
#         self.user_id = user_id


# @patch
# class DatasetSZ(Serializer):
#     class Meta:
#         model = Dataset
#         read_only_fields = {"id", "user_id"}


# # Turns out we need to create a patch for every tweaked use of our model, we cannot change it on the fly.
# # See https://github.com/swagger-api/swagger-core/issues/1863#issuecomment-237339565
# @patch
# class DatasetSZPost(Serializer):
#     class Meta:
#         model = Dataset
#         # user_domain_labels are currently not needed on the client
#         exclude = {"project_links", "preview"}
#         read_only_fields = {"id", "user_id"}
