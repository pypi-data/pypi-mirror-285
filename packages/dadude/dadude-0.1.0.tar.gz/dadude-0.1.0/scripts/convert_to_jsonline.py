import duckdb


if __name__ == "__main__":
    client = duckdb.connect(database=':memory:', read_only=False)
    client.execute("")