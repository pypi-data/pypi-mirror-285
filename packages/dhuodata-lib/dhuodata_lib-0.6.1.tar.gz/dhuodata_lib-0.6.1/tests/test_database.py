from sqlalchemy import text
from dhuolib.repository import DatabaseConnection, GenericRepository
import unittest
import sys
import pandas as pd

sys.path.append("src")


class TestDatabaseConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_file_name = "tests/files/database.json"
        cls.db_connection = DatabaseConnection(config_file_name=cls.config_file_name)

    def test_database_connection_init(self):
        db_connection = DatabaseConnection(self.config_file_name)
        self.assertIsNotNone(db_connection.engine)
        self.assertIsNotNone(db_connection.session)

    def test_session_scope(self):
        with self.db_connection.session_scope() as session:
            self.assertIsNotNone(session)


class TestGenericRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_file_name = "tests/files/database.json"
        cls.db_connection = DatabaseConnection(config_file_name=cls.config_file_name)
        cls.table_name = "test_table"
        cls.repo = GenericRepository(db_connection=cls.db_connection)
        cls.repo.db.session.execute(
            text(
                f"CREATE TABLE IF NOT EXISTS {cls.table_name} (id INTEGER PRIMARY KEY, name VARCHAR(255), age INTEGER, predict VARCHAR(255), version VARCHAR(255), created_at TIMESTAMP)"
            )
        )

    @classmethod
    def tearDownClass(cls):
        with cls.db_connection.session_scope() as session:
            session.execute(text(f"DROP TABLE IF EXISTS {cls.table_name}"))

    def setUp(self):
        self.db_connection = self.__class__.db_connection
        self.repo = self.__class__.repo
        self.table_name = self.__class__.table_name

    def tearDown(self):
        with self.db_connection.session_scope() as session:
            session.execute(text(f"DELETE FROM {self.table_name}"))

    def test_1_insert(self):
        data = {"id": 1, "name": "John Doe", "age": 30}
        inserted = self.repo.insert(self.table_name, data)
        with self.repo.db.session_scope() as session:
            result = session.execute(
                text(f"SELECT * FROM {self.table_name} WHERE id=1")
            ).fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result.name, "John Doe")
            self.assertEqual(result.age, 30)
            self.assertEqual(inserted.name, "John Doe")
            self.assertEqual(inserted.age, 30)

    def test_2_deve_falhar_a_insercao_de_dados_invalidos(self):
        invalid_data = {"id": 1, "invalid_column": "Invalid Data"}
        with self.assertRaises(Exception):
            self.repo.insert(self.table_name, invalid_data)

    def test_3_deve_retornar_um_value_error_quando_o_nome_da_tabela_for_vazio(self):
        with self.assertRaises(ValueError):
            self.repo.insert("", {})

    def test_4_get_items_with_pagination(self):
        for i in range(10):
            data = {"id": i + 1, "name": f"User {i+1}", "age": 20 + i}
            self.repo.insert(self.table_name, data)

        items = self.repo.get_items_with_pagination(self.table_name, 1, 5)
        self.assertEqual(len(items["items"]), 5)
        self.assertEqual(items["items"][0].name, "User 1")
        self.assertEqual(items["items"][4].name, "User 5")

        items = self.repo.get_items_with_pagination(self.table_name, 2, 5)
        self.assertEqual(len(items["items"]), 5)
        self.assertEqual(items["items"][0].name, "User 6")
        self.assertEqual(items["items"][4].name, "User 10")

    def test_5_update(self):
        data = {"id": 1, "name": "John Doe", "age": 30, "predict": "Negative"}
        self.repo.insert(table_name=self.table_name, data=data)

        updated_data = {"id": 1, "name": "John Doe", "age": 30, "predict": "Positive"}
        self.repo.update(
            table_name=self.table_name,
            index=updated_data["id"],
            predict=updated_data["predict"],
        )

        with self.repo.db.session_scope() as session:
            result = session.execute(
                text(
                    f"SELECT * FROM {self.table_name} WHERE id={int(updated_data['id'])}"
                )
            ).fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result.predict, "Positive")
            self.assertEqual(result.name, "John Doe")

    def test_6_insert_invalid_data(self):
        invalid_data = {"id": 1, "invalid_column": "Invalid Data"}
        with self.assertRaises(Exception):
            self.repo.insert(self.table_name, invalid_data)

    def test_7_update_table_by_dataframe(self):
        initial_data = pd.DataFrame(
            [{"id": 1, "name": "John Doe", "age": 30, "predict": "Positive"}]
        )
        self.repo.update_table_by_dataframe(
            table_name=self.table_name,
            df_predict=initial_data,
            if_exists="replace",
            is_update_version=True,
        )

        new_data = pd.DataFrame(
            [
                {
                    "id": 2,
                    "name": "Jane Doe",
                    "age": 25,
                    "predict": "Positive",
                    "version": 1,
                    "created_at": "2021-01-01",
                },
                {
                    "id": 3,
                    "name": "Jim Beam",
                    "age": 35,
                    "predict": "Negative",
                    "version": 1,
                    "created_at": "2021-01-01",
                },
            ]
        )
        self.repo.update_table_by_dataframe(self.table_name, new_data)

        df = self.repo.to_dataframe(self.table_name)
        self.assertEqual(len(df), 3)
        self.assertListEqual(list(df["name"]), ["John Doe", "Jane Doe", "Jim Beam"])
        self.assertListEqual(list(df["predict"]), ["Positive", "Positive", "Negative"])

    def test_8_create_table_by_dataframe(self):
        with self.db_connection.session_scope() as session:
            session.execute(text(f"DROP TABLE IF EXISTS {self.table_name}"))
        data = pd.DataFrame(
            [
                {
                    "id": 1,
                    "name": "John Doe",
                    "age": 30,
                    "predict": "Positive",
                    "score": 0.932,
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "age": 25,
                    "predict": "Negative",
                    "score": 0.1332,
                },
                {
                    "id": 3,
                    "name": "Bob Johnson",
                    "age": 35,
                    "predict": "Positive",
                    "score": 0.53,
                },
            ]
        )
        self.repo.create_table_by_dataframe(self.table_name, data)
        with self.repo.db.session_scope() as session:
            result = session.execute(
                text(f"SELECT * FROM {self.table_name}")
            ).fetchall()
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0].name, "John Doe")
            self.assertEqual(result[1].name, "Jane Smith")
            self.assertEqual(result[2].name, "Bob Johnson")

    def test_9_update_table_by_dataframe_with_versioning(self):
        with self.repo.db.session_scope() as session:
            session.execute(text(f"DROP TABLE {self.table_name}"))
        data = pd.DataFrame(
            [
                {
                    "id": 1,
                    "name": "John Doe",
                    "age": 30,
                    "predict": "",
                    "created_at": "2021-01-01",
                    "version": 1,
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "age": 25,
                    "predict": "",
                    "created_at": "2021-01-01",
                    "version": 1,
                },
                {
                    "id": 3,
                    "name": "Bob Johnson",
                    "age": 35,
                    "created_at": "2021-01-01",
                    "version": 1,
                    "predict": "",
                },
            ]
        )
        response = self.repo.create_table_by_dataframe(self.table_name, data)
        self.assertEqual(response["number_lines_inserted"], 3)

        update_data = pd.DataFrame(
            [
                {"id": 1, "name": "John Doe", "age": 30, "predict": "Positive"},
                {"id": 2, "name": "Jane Smith", "age": 25, "predict": "Positive"},
                {"id": 3, "name": "Bob Johnson", "age": 35, "predict": "Negative"},
            ]
        )

        self.repo.update_table_by_dataframe(
            table_name=self.table_name,
            df_predict=update_data,
            if_exists="replace",
            is_update_version=True,
        )

        df = self.repo.to_dataframe(self.table_name)
        self.assertEqual(len(df), 3)
        self.assertListEqual(
            list(df["name"]), ["John Doe", "Jane Smith", "Bob Johnson"]
        )
        self.assertListEqual(list(df["predict"]), ["Positive", "Positive", "Negative"])
        self.assertListEqual(list(df["version"]), [2, 2, 2])
