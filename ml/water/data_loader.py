import pandas as pd
import psycopg2


# ============================================================
# LOAD DATA FROM PANDAS DATAFRAME
# ============================================================

def load_from_dataframe(data):

    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            "Input must be a pandas DataFrame."
        )

    return data.copy()


# ============================================================
# LOAD DATA FROM CSV
# ============================================================

def load_from_csv(file_path):

    data = pd.read_csv(file_path)

    return data


# ============================================================
# LOAD DATA FROM POSTGRESQL
# ============================================================

def load_from_postgresql(
    host,
    port,
    database,
    user,
    password,
    query
):

    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    try:

        data = pd.read_sql(
            query,
            connection
        )

    finally:

        connection.close()

    return data