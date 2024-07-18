from fire import Fire
import duckdb


def csv2json(csv_path: str) -> str:
    target_json_path = csv_path.replace(".csv", ".json")
    con = duckdb.connect(database=":memory:")
    con.execute(
        f"copy (SELECT * FROM read_csv('{csv_path}')) to '{target_json_path}'"
    )
    con.close()
    return target_json_path


def csv2parquet(csv_path: str) -> str:
    target_parquet_path = csv_path.replace(".csv", ".parquet")
    con = duckdb.connect(database=":memory:")
    con.execute(
        f"copy (SELECT * FROM read_csv('{csv_path}')) to '{target_parquet_path}'"
    )
    con.close()
    return target_parquet_path


def json2parquet(json_path: str) -> str:
    target_parquet_path = json_path.replace(".json", ".parquet")
    con = duckdb.connect(database=":memory:")
    con.execute(
        f"copy (SELECT * FROM read_json('{json_path}')) to '{target_parquet_path}'"
    )
    con.close()
    return target_parquet_path


if __name__ == "__main__":
    Fire()