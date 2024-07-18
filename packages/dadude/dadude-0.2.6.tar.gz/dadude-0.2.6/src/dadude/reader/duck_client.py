from typing import Callable
import duckdb


class Quack:
    """
    Unified Duckdb client. (incomplete)
    For unsafe usage, just use _sql.
    """

    def __init__(self, db_path: str = ":memory:", read_only: bool = False):
        self.db_path = db_path
        self.client = duckdb.connect(database=db_path, read_only=read_only)

    def _sql(self, query, limit=None, filters=None, mode="df"):
        query = query.strip()
        query = query.replace(";", "")
        if filters is not None:
            query += " WHERE " + " AND ".join(filters)
        if limit is not None:
            query += " LIMIT " + str(limit)
        print(query)
        if mode == "df":
            return self.client.execute(query + ";").df()
        else:
            return self.client.execute(query + ";").arrow()

    def create_table(self, table_name, file_path):  # , format="parquet"
        # if file_path.endswith(".csv"):
        #     format = "csv"
        #     read_query = "read_csv"
        # elif file_path.endswith(".json"):
        #     format = "json"
        #     read_query = "read_json"
        # else:
        #     if format == "parquet":
        #         read_query = "read_parquet"

        self._sql(f"CREATE TABLE '{table_name}' AS SELECT * FROM '{file_path}'")

    def create_function(self, func_name: str, func: Callable):
        self.client.create_function(func_name, func)

    def inspect_parquet_metadata(self, file_path):
        return self._sql(f"FROM parquet_metadata('{file_path}')")

    def inspect_parquet_schema(self, file_path):
        return self._sql(f"FROM parquet_schema('{file_path}')")

    def get_table(self, table_name):
        return self.client.table(table_name)

    def to_pandas(self, table_name):
        return self.get_table(table_name).df()

    def to_csv(self, query, target_file_path, header=True, sep=","):
        dump_query = f"COPY ({query}) TO '{target_file_path}' (FORMAT CSV, HEADER={header}, DELIMITER='{sep}');"
        return self._sql(dump_query)

    def to_parquet(self, query, target_file_path):
        dump_query = f"COPY ({query}) TO '{target_file_path}' (FORMAT PARQUET);"
        return self._sql(dump_query)

    def list_tables(self):
        return self._sql("SHOW tables;")

    def schema(self, table):
        return self._sql(f"DESC {table}")

    def describe(self, table):
        return self._sql(f"SUMMARIZE {table}")

    def count(self, table):
        return self._sql(f"SELECT COUNT(*) count_{table} FROM {table};")

    def select(self, table, limit=None, columns="*"):
        if isinstance(columns, list):
            columns = ", ".join(columns)
        return self._sql(f"SELECT {columns} FROM {table}", limit)

    def distinct(self, table, column=None):
        if column is None:
            column = self.schema.iloc[0, 0]
        return self._sql(f"SELECT DISTINCT {column} FROM {table};")

    def head(self, table, top=5):
        return self._sql(f"FROM {table};", top)

    def sample(self, table, n_samples=5):
        return self._sql(f"FROM {table} TABLESAMPLE {n_samples} ROWS;")
