from enum import Enum
from loguru import logger

# import pyarrow.dataset as ds
import pandas as pd
from deltalake.data_catalog import DataCatalog
from deltalake import write_deltalake

from ..config import default_storage_config


logger = logger.bind(name=__name__)
catalog = DataCatalog.UNITY


class DeltaWriterMode(str, Enum):
    OVERWRITE = "overwrite"
    APPEND = "append"
    IGNORE = "ignore"
    ERROR = "error"


class DeltaStorageTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    INBOX = "inbox"
    EVALUATION = "evaluation"
    STAGING = "staging"


class DeltaWriterError(Exception):
    pass


class DeltaWriter:
    def __init__(self, bucket: str = "matter-most") -> None:
        self.catalog = catalog
        self.storage_options = default_storage_config
        self.bucket_path = f"s3a://{bucket}"

    def _write(
        self,
        resource_path: str,
        table: pd.DataFrame,
        mode: DeltaWriterMode = DeltaWriterMode.ERROR,
    ):
        logger.debug(f"Start: writing data to {resource_path}.")
        try:
            write_deltalake(
                resource_path,
                table,
                storage_options=self.storage_options,
                mode=mode,  # type: ignore
            )
        except Exception as e:
            logger.error(f"Error: {e}.")
            raise DeltaWriterError(e)

    def write_json(
        self,
        json_file_path: str,
        lines=False,
        mode: DeltaWriterMode = DeltaWriterMode.ERROR,
    ):
        tier = DeltaStorageTier(json_file_path.split("/")[-2]).value
        table_name = json_file_path.split("/")[-1].split(".")[0]
        lake_path = f"{self.bucket_path}/{tier}/{table_name}"
        # load json file into pyarrow table
        df = pd.read_json(json_file_path, lines=lines)
        logger.info(f"View: {df.head(1)}")
        self._write(lake_path, df, mode)
        logger.info(f"Done: {table_name=} written to {lake_path=}.")


def write_json_table(
    local_json_file_path: str, mode: DeltaWriterMode = DeltaWriterMode.ERROR
):
    writer = DeltaWriter()
    writer.write_json(local_json_file_path, mode=mode)


def write_nljson_table(
    local_json_file_path: str, mode: DeltaWriterMode = DeltaWriterMode.ERROR
):
    writer = DeltaWriter()
    writer.write_json(local_json_file_path, lines=True, mode=mode)
