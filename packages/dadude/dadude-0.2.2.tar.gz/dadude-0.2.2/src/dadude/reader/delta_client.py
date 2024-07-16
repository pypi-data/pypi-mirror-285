import pandas as pd
from deltalake import DeltaTable
# from deltalake.data_catalog import DataCatalog

from ..config import default_storage_config


def read_delta_table(path: str) -> pd.DataFrame:
    dt = DeltaTable(path, storage_options=default_storage_config)
    return dt.to_pandas()


def read_delta_table_from_catalog():
    raise NotImplementedError
    # return DeltaTable.from_data_catalog(
    #     data_catalog=DataCatalog.UNITY,
    #     database_name="materials",
    #     table_name="property_entity",
    # )

