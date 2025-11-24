import os
from typing import Literal, Optional, Union

import psycopg2
from psycopg2.extras import RealDictCursor


class DBConnector:
    def __init__(self, config=None, test=False):
        if config is not None:
            self.host = config["host"]
            self.port = config["post"]
            self.database = config["database"]
            self.user = config["user"]
            self.password = config["password"]
            self.schema = config["schema"]
        else:
            self.host = os.environ["POSTGRES_HOST"]
            self.port = os.environ["POSTGRES_PORT"]
            self.database = os.environ["POSTGRES_DATABASE"]
            self.user = os.environ["POSTGRES_USER"]
            self.password = os.environ["POSTGRES_PASSWORD"]
            if test:
                self.schema = os.environ["POSTGRES_SCHEMA_TEST"]
            else:
                self.schema = os.environ["POSTGRES_SCHEMA"]

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Union[Literal["one"], Literal["all"], Literal["none"]] = "one",
    ):
        try:
            with psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                options=f"-c search_path={self.schema}",
                cursor_factory=RealDictCursor,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, data)
                    if return_type == "one":
                        return cursor.fetchone()
                    if return_type == "all":
                        return cursor.fetchall()
        except Exception as e:
            print("ERROR")
            print(e)
            raise e
