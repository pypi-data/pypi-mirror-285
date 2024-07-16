from enum import Enum

import os
from dotenv import load_dotenv
from pathlib import Path
from loguru import logger

# import pyarrow.dataset as ds
import pandas as pd
from deltalake.data_catalog import DataCatalog
from deltalake import write_deltalake


logger = logger.bind(name=__name__)
catalog = DataCatalog.UNITY


class DeltaWriterMode(str, Enum):
    OVERWRITE = "overwrite"
    APPEND = "append"
    IGNORE = "ignore"
    ERROR = "error"


class DeltaWriterError(Exception):
    pass


class DeltaWriter:
    def __init__(self) -> None:
        load_dotenv()
        self.catalog = catalog
        self.storage_options = {
            "AWS_ACCESS_KEY_ID": os.getenv("STORAGE_ACCESS_KEY_ID", ""),
            "AWS_SECRET_ACCESS_KEY": os.getenv("STORAGE_SECRET_ACCESS_KEY", ""),
            "AWS_ENDPOINT_URL": os.getenv("STORAGE_ENDPOINT_URL", ""),
            "AWS_REGION": "local",
            "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
            "AWS_ALLOW_HTTP": "true",
        }

    def _write(
        self,
        lake_path: str,
        table: pd.DataFrame,
        mode: DeltaWriterMode = DeltaWriterMode.ERROR,
    ):
        logger.debug(f"Start: writing data to {lake_path}.")
        try:
            write_deltalake(
                lake_path,
                table,
                storage_options=self.storage_options,
                mode=mode,  # type: ignore
            )
            logger.info(f"Done: {table.Name=} written to {lake_path=}.")
        except Exception as e:
            logger.error(f"Error: {e}.")
            raise DeltaWriterError(e)

    def write_json(
        self,
        json_file_path: str,
        lake_path: str,
        mode: DeltaWriterMode = DeltaWriterMode.ERROR,
    ):
        # load json file into pyarrow table
        df = pd.read_json(json_file_path, lines=False)
        self._write(lake_path, df, mode)


if __name__ == "__main__":
    local_property_entity_path = "/home/kevinxu/arch/dadude/data/gold/material_property_entity_v3.json"
    lake_path = "s3a://test/property/"
    writer = DeltaWriter()
    writer.write_json(
        local_property_entity_path,
        lake_path,
    )