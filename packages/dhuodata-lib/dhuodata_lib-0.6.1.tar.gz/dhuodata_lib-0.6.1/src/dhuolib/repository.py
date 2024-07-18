import json
import sys
import pandas as pd

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, inspect, Float, Integer, text
from sqlalchemy.types import VARCHAR
from sqlalchemy.dialects.oracle import FLOAT as OracleFLOAT
from sqlalchemy.orm import scoped_session, sessionmaker

from dhuolib.config import logger


class DatabaseConnection:
    def __init__(self, config_file_name=None):
        if self.in_dataflow():
            self.connection_string = f"oracle+oracledb://{sys.argv[1]}"
        else:
            f = open(config_file_name)
            data = json.load(f)
            self.connection_string = data["connection_string"]

        self.engine = self._get_engine(self.connection_string)
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def in_dataflow(self):
        if str(Path.home()) == "/home/dataflow":
            return True
        return False

    def _get_engine(self, connection_string):
        self.engine = create_engine(connection_string)
        return self.engine

    @contextmanager
    def session_scope(self, expire=False):
        self.session.expire_on_commit = expire
        try:
            yield self.session
            logger.info(f"Sessão foi iniciada {self.session}")
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro na sessão {self.session}: {e}")
            raise
        finally:
            self.session.close()
            logger.info(f"Sessão foi finalizada {self.session}")


class GenericRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def map_dtype(self, df, engine):
        dtype_mapping = {}
        for col, dtype in df.dtypes.items():
            if pd.api.types.is_integer_dtype(dtype):
                dtype_mapping[col] = Integer()
            elif pd.api.types.is_float_dtype(dtype):
                if engine.dialect.name == "oracle":
                    dtype_mapping[col] = Float(precision=53).with_variant(
                        OracleFLOAT(binary_precision=53), "oracle"
                    )
                else:
                    dtype_mapping[col] = Float()
            elif dtype == "object":
                dtype_mapping[col] = VARCHAR(255)
            else:
                dtype_mapping[col] = VARCHAR(255)
        return dtype_mapping

    def create_table_by_dataframe(self, table_name: str, df: pd.DataFrame):
        if not table_name or df.empty:
            raise ValueError("table_name or data is required")

        with self.db.session_scope() as session:
            inspector = inspect(session.bind)
            if table_name in inspector.get_table_names():
                return f"A tabela {table_name} já existe. Utilize o método update_table_by_dataframe para atualizar a tabela."

            dtype_mapping = self.map_dtype(df, session.bind)

            num_rows_inserted = df.to_sql(
                name=table_name,
                con=session.bind,
                if_exists="replace",
                index=False,
                dtype=dtype_mapping,
            )

        return {"number_lines_inserted": num_rows_inserted, "table_name": table_name}

    def insert(self, table_name: str, data: dict):

        if not table_name or not data:
            raise ValueError("table_name and data is required")

        with self.db.session_scope() as session:
            columns = ", ".join(data.keys())
            values = ", ".join([f":{key}" for key in data.keys()])
            query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")
            session.execute(query, data)
            inserted_predict = session.execute(
                text(
                    f"SELECT * FROM {table_name} WHERE id = (SELECT MAX(id) FROM {table_name})"
                )
            ).fetchone()
        return inserted_predict

    # replace_or_append tabela na base de dados
    def update_table_by_dataframe(
        self,
        table_name: str,
        df_predict: pd.DataFrame,
        if_exists: str = "append",
        is_update_version: bool = False,
    ):

        if not table_name or df_predict.empty:
            raise ValueError("table_name, df_predict are required")
        with self.db.session_scope() as session:
            if is_update_version:
                df = pd.read_sql(
                    f"SELECT version FROM {table_name.lower()}", con=session.bind
                )
                latest_version = df["version"].max()
                if pd.isna(latest_version):
                    latest_version = 1
                else:
                    latest_version = int(latest_version) + 1

                df_predict["version"] = latest_version
                df_predict["created_at"] = datetime.now()

                df_predict["created_at"] = pd.to_datetime(df_predict["created_at"])
            df_predict.to_sql(
                name=table_name, con=session.bind, if_exists=if_exists, index=False
            )

    def get_items_with_pagination(
        self, table_name: str, page: int = 1, page_size: int = 10000
    ):

        if not table_name:
            raise ValueError("table_name is required")

        offset = (page - 1) * page_size
        items = []
        with self.db.session_scope() as session:
            query = text(
                f"SELECT * FROM {table_name} ORDER BY id LIMIT :limit OFFSET :offset"
            )
            items = session.execute(
                query, {"offset": offset, "limit": page_size}
            ).fetchall()

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_items": len(items),
        }

    def to_dataframe(
        self,
        table_name: str = None,
        filter_clause: str = None,
        list_columns: list = None,
    ):
        if not table_name:
            raise ValueError("table_name and list_columns are required")
        columns = ""
        df = None
        query = ""

        if list_columns:
            columns = ", ".join([column for column in list_columns])
        else:
            columns = "*"

        if filter_clause:
            query = f"SELECT {columns} FROM {table_name} WHERE {filter_clause}"
        else:
            query = f"SELECT {columns} FROM {table_name}"

        with self.db.session_scope() as session:
            df = pd.read_sql(query, con=session.bind)
        return df

    def get_by_id(self, table_name: str, id: int):
        if not table_name or not id:
            raise ValueError("table_name and id are required")
        with self.db.session_scope() as session:
            query = text(f"SELECT * FROM {table_name} WHERE id = :id")
            item = session.execute(query, {"id": id}).fetchone()
        return item

    def get_all(self, table_name: str):
        if not table_name:
            raise ValueError("table_name is required")
        with self.db.session_scope() as session:
            query = text(f"SELECT * FROM {table_name}")
            items = session.execute(query).fetchall()
        return items

    def update(self, table_name: str, index: int, predict: str):
        if not table_name or not index or not predict:
            raise ValueError("table_name, index and predict are required")
        with self.db.session_scope() as session:
            update_query = text(
                f"UPDATE {table_name} SET predict = :predict WHERE id = :id"
            )
            session.execute(update_query, {"id": int(index), "predict": predict})
            updated_predict = session.execute(
                text(
                    f"SELECT * FROM {table_name} WHERE id = (SELECT MAX(id) FROM {table_name})"
                )
            ).fetchone()
        return updated_predict
