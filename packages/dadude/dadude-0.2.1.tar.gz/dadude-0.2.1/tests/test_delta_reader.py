import pytest
import pandas as pd
from dadude.reader.delta_client import read_delta_table


@pytest.fixture
def qa_table_path():
    return "s3://test/property"

def test_read_delta_table(qa_table_path):
    df = read_delta_table(qa_table_path)
    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) == {
        "ppi_id",
        "class_ii_name",
        "print_friendly_units",
        "statistical_type",
        "upper_bound",
        "class_i_name",
        "lower_bound",
        "created_at",
        "display_name_en",
        "application_domain",
        "domain_id",
        "domain_name_cn",
        "parent_ppi_id",
        "alias_list_en",
        "class_iii_name",
        "updated_at",
        "display_name_cn",
        "unit_recognition",
        "alias_list_cn",
    }
    assert len(df) == 1383
