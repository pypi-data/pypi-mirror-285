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


class DeltaWriterSchemaMode(str, Enum):
    MERGE = "merge"
    OVERWRITE = "overwrite"


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
        logger.warning(f"Mode: {mode}.")
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

    def _write_with_schema_mode(
        self,
        resource_path: str,
        table: pd.DataFrame,
        data_mode: DeltaWriterMode,
        schema_mode: DeltaWriterSchemaMode = DeltaWriterSchemaMode.MERGE,
    ):
        # TODO: this should not be a separate function
        logger.warning("Check: entering schema merge mode.")
        logger.debug(f"Start: writing data to {resource_path}.")
        logger.warning(f"Mode: {data_mode=}, {schema_mode=}.")
        try:
            write_deltalake(
                resource_path,
                table,
                storage_options=self.storage_options,
                mode=data_mode,  # type: ignore
                schema_mode=schema_mode,  # type: ignore
                engine="rust",
            )
        except Exception as e:
            logger.error(f"Error: {e}.")
            raise DeltaWriterError(e)

    def write_json(
        self,
        json_file_path: str,
        lines=False,
        mode: DeltaWriterMode = DeltaWriterMode.ERROR,
        schema_mode: DeltaWriterSchemaMode | None = None,
    ):
        tier = DeltaStorageTier(json_file_path.split("/")[-2]).value
        table_name = json_file_path.split("/")[-1].split(".")[0]
        lake_path = f"{self.bucket_path}/{tier}/{table_name}"
        # TODO: load json file into pyarrow table with schema inference
        # we use pd.DataFrame for now
        df = pd.read_json(json_file_path, lines=lines)
        logger.info(f"View: {df.head(1)}")
        if schema_mode is not None:
            self._write_with_schema_mode(lake_path, df, mode, schema_mode)
        else:
            self._write(lake_path, df, mode)
        logger.info(f"Done: {table_name=} written to {lake_path=}.")


def write_json_table(
    local_json_file_path: str,
    lines: bool = False,
    mode: DeltaWriterMode = DeltaWriterMode.ERROR,
):
    writer = DeltaWriter()
    writer.write_json(local_json_file_path, lines=lines, mode=mode)


def overwrite_json_table(
    local_json_file_path: str,
    lines: bool = False,
    mode: DeltaWriterMode = DeltaWriterMode.OVERWRITE,
):
    writer = DeltaWriter()
    writer.write_json(
        local_json_file_path,
        lines=lines,
        mode=mode,
        schema_mode=DeltaWriterSchemaMode.OVERWRITE,
    )
