from fastapi import FastAPI

from fa_common import StorageType, get_settings, logger

from .base_client import BaseClient

# from minio.error import ResponseError


def setup_storage(app: FastAPI) -> None:
    settings = get_settings()
    if settings.STORAGE_TYPE == StorageType.MINIO:
        from miniopy_async import Minio
        from miniopy_async.credentials import IamAwsProvider, StaticProvider

        if settings.STORAGE_ENDPOINT is None:
            raise ValueError("Minio endpoint missing from env variables")

        # Minio has a `ChainedProvider` class which should allow us to define multiple options however
        # it doesn't appear to work properly?
        if settings.STORAGE_ACCESS_KEY is None and settings.STORAGE_SECRET_KEY is None:
            logger.info("Storage set to Minio using IAM AWS authentication")
            credential_provider = IamAwsProvider()

        # @REVIEW: Below is added for local testing (temporary creds).
        elif (
            settings.STORAGE_ACCESS_TOKEN is not None and settings.STORAGE_ACCESS_TOKEN != "" and settings.STORAGE_SECRET_VALUE is not None
        ):
            logger.info("Storage set to Minio using temporary creds with access token.")
            credential_provider = StaticProvider(
                settings.STORAGE_ACCESS_KEY,
                settings.STORAGE_SECRET_VALUE.get_secret_value(),
                settings.STORAGE_ACCESS_TOKEN,
            )
        else:
            if settings.STORAGE_ACCESS_KEY is None or settings.STORAGE_SECRET_VALUE is None:
                raise ValueError("Missing minio settings from env variables")
            else:
                logger.info("Storage set to Minio using access/secret key authentication")
                credential_provider = StaticProvider(settings.STORAGE_ACCESS_KEY, settings.STORAGE_SECRET_VALUE.get_secret_value())

        minio_client = Minio(
            settings.STORAGE_ENDPOINT,
            credentials=credential_provider,
            secure=settings.STORAGE_SSL,
        )

        app.minio = minio_client  # type: ignore
    elif settings.STORAGE_TYPE in [
        StorageType.GCP_STORAGE,
        StorageType.FIREBASE_STORAGE,
    ]:
        from google.cloud.storage import Client as GCPClient

        # Uses GOOGLE_APPLICATION_CREDENTIALS Env Var
        gcp_storage_client = GCPClient()
        app.gcp_storage = gcp_storage_client  # type: ignore
    elif settings.STORAGE_TYPE == StorageType.LOCALFS_STORAGE:
        if settings.LOCALFS_STORAGE_PATH is not None:
            import os
            from pathlib import Path

            storage_path = Path(settings.LOCALFS_STORAGE_PATH)
            if storage_path.exists() is False:
                try:
                    os.makedirs(storage_path)
                except OSError as err:
                    raise ValueError("Could not create directory for local storage") from err
            elif storage_path.is_file():
                raise ValueError("A local file was specified as the storage directory")
            app.storage_root_path = storage_path
        else:
            raise ValueError("Missing local fs storage path from env variables")
        logger.info(f"Storage set to local filesystem at {settings.LOCALFS_STORAGE_PATH}")
    elif settings.STORAGE_TYPE == StorageType.NONE:
        logger.info("Storage set to NONE and cannot be used")
        return
    else:
        raise ValueError("STORAGE_TYPE Setting is not a valid storage option.")


def get_storage_client() -> BaseClient:
    if get_settings().STORAGE_TYPE == StorageType.MINIO:
        from .minio_client import MinioClient

        return MinioClient()
    elif get_settings().STORAGE_TYPE == StorageType.GCP_STORAGE:
        from .gcp_client import GoogleStorageClient

        return GoogleStorageClient()
    elif get_settings().STORAGE_TYPE == StorageType.FIREBASE_STORAGE:
        from .gcp_client import FirebaseStorageClient

        return FirebaseStorageClient()
    elif get_settings().STORAGE_TYPE == StorageType.LOCALFS_STORAGE:
        from .localfs_client import LocalFSClient

        return LocalFSClient()

    raise ValueError("STORAGE_TYPE Setting is not a valid storage option.")
