import os
from unittest.mock import MagicMock, patch

import pytest

from src.DAO.DBConnector import DBConnector


@pytest.fixture
def mock_env_vars():
    return {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": "test_db",
        "POSTGRES_USER": "user",
        "POSTGRES_PASSWORD": "password",
        "POSTGRES_SCHEMA": "public",
        "POSTGRES_SCHEMA_TEST": "test_schema",
    }


@pytest.fixture
def db_config():
    return {
        "host": "custom_host",
        "post": "5433",
        "database": "custom_db",
        "user": "custom_user",
        "password": "custom_password",
        "schema": "custom_schema",
    }


def test_init_with_config_dict(db_config):
    """Tests initialization using a configuration dictionary."""
    connector = DBConnector(config=db_config)

    assert connector.host == "custom_host"
    assert connector.port == "5433"
    assert connector.database == "custom_db"
    assert connector.user == "custom_user"
    assert connector.password == "custom_password"
    assert connector.schema == "custom_schema"


def test_init_with_env_vars(mock_env_vars):
    """Tests initialization using environment variables (default)."""
    with patch.dict(os.environ, mock_env_vars):
        with patch("src.DAO.DBConnector.load_dotenv"):
            connector = DBConnector()

            assert connector.host == "localhost"
            assert connector.schema == "public"


def test_init_with_env_vars_test_mode(mock_env_vars):
    """Tests initialization in test mode to switch schemas."""
    with patch.dict(os.environ, mock_env_vars):
        with patch("src.DAO.DBConnector.load_dotenv"):
            connector = DBConnector(test=True)

            assert connector.schema == "test_schema"


@patch("psycopg2.connect")
def test_sql_query_return_one(mock_connect, db_config):
    """Tests sql_query returning a single result."""
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value

    expected_result = {"id": 1, "name": "Test"}
    mock_cursor.fetchone.return_value = expected_result

    connector = DBConnector(config=db_config)
    result = connector.sql_query("SELECT * FROM table", return_type="one")

    assert result == expected_result
    mock_cursor.execute.assert_called_once_with("SELECT * FROM table", None)
    mock_cursor.fetchone.assert_called_once()


@patch("psycopg2.connect")
def test_sql_query_return_all(mock_connect, db_config):
    """Tests sql_query returning multiple results."""
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value

    expected_result = [{"id": 1}, {"id": 2}]
    mock_cursor.fetchall.return_value = expected_result

    connector = DBConnector(config=db_config)
    result = connector.sql_query("SELECT * FROM table", return_type="all")

    assert result == expected_result
    mock_cursor.execute.assert_called_once_with("SELECT * FROM table", None)
    mock_cursor.fetchall.assert_called_once()


@patch("psycopg2.connect")
def test_sql_query_with_data(mock_connect, db_config):
    """Tests sql_query with parameters passed to execute."""
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value

    connector = DBConnector(config=db_config)
    query = "INSERT INTO table (col) VALUES (%s)"
    data = ("value",)

    connector.sql_query(query, data=data, return_type=None)

    mock_cursor.execute.assert_called_once_with(query, data)


@patch("psycopg2.connect")
def test_sql_query_exception_handling(mock_connect, db_config):
    """Tests that exceptions are caught, logged, and re-raised."""
    mock_conn = mock_connect.return_value.__enter__.return_value
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value

    class MockDatabaseError(Exception):
        def __init__(self, msg):
            super().__init__(msg)
            self.pgcode = "23505"
            self.diag = MagicMock()
            self.diag.constraint_name = "unique_violation"

    db_error = MockDatabaseError("Connection failed")
    mock_cursor.execute.side_effect = db_error

    connector = DBConnector(config=db_config)

    with pytest.raises(MockDatabaseError):
        connector.sql_query("SELECT * FROM fail")
