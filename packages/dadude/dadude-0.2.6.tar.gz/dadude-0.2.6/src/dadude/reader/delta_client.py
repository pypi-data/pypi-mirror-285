from loguru import logger
import pandas as pd
from deltalake import DeltaTable
# from deltalake.data_catalog import DataCatalog

from ..config import default_storage_config


logger = logger.bind(name=__name__)


class DeltaClientError(Exception):
    """Base class for exceptions in this module."""

    pass


def read_delta_table(path: str) -> pd.DataFrame:
    try:
        dt = DeltaTable(path, storage_options=default_storage_config)
    except Exception as e:
        logger.error(f"Error reading DeltaTable: {e}")
        raise DeltaClientError(f"Error reading DeltaTable: {e}")
    return dt.to_pandas()


def read_delta_table_from_catalog():
    raise NotImplementedError
    # return DeltaTable.from_data_catalog(
    #     data_catalog=DataCatalog.UNITY,
    #     database_name="materials",
    #     table_name="property_entity",
    # )


# TODO: add reading from local cache