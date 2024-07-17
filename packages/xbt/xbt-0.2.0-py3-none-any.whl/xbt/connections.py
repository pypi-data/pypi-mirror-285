import duckdb


def build_connection(conn):
    if conn["type"] == "duckdb":
        db = duckdb.connect(conn["path"])
        return db
