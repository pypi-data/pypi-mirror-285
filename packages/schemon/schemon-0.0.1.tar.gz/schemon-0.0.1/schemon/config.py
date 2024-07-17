import os
from schemon.env import loadenv

loadenv()


class Config:
    """
    Configuration class for database connection settings.
    Supported engine:
    - sqlite3
    - databricks

    Pending engine:
    - sqlitecloud: it's not yet supported - https://github.com/sqlitecloud/sqlitecloud-py/issues/2
    """

    if os.getenv("DB_TYPE") == "sqlite3":
        database_uri = os.getenv("DATABASE_URL")
        connect_args = {}
    elif os.getenv("DB_TYPE") == "mysql":
        database_uri = os.getenv("DATABASE_URL")
        connect_args = {'ssl_ca': os.getenv("DATABASE_CERTIFICATE_PATH")}
    elif os.getenv("DB_TYPE") == "databricks":
        access_token = os.getenv("DATABRICKS_TOKEN")
        server_hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
        sql_warehouse_http_path = os.getenv("DATABRICKS_SQL_WAREHOUSE_HTTP_PATH")
        catalog = os.getenv("DATABRICKS_CATALOG")
        schema = os.getenv("DATABRICKS_SCHEMA")

        database_uri = f"databricks://token:{access_token}@{server_hostname}?http_path={sql_warehouse_http_path}&catalog={catalog}&schema={schema}"
        connect_args = {"_tls_verify_hostname": True}
    else:
        raise ValueError("DB_TYPE is not supported")
    show_sql = os.getenv("SHOW_SQL") == "1"


config = Config
