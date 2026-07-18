import pytest

from connections.mysql_connection import MySQLDatabase
from connections.oracle_connection import OracleDatabase
from utils.config_reader import ConfigReader


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.mysql
def test_mysql_database_connection() -> None:
    """Verify that the configured MySQL target database is accessible."""

    database = MySQLDatabase()
    connection = database.connect()
    expected_database = ConfigReader().get_mysql_config()["database"]

    try:
        assert connection.is_connected(), (
            "MySQL database connection was not established."
        )

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE(), VERSION()")
        result = cursor.fetchone()
        cursor.close()

        assert result is not None

        actual_database, mysql_version = result

        assert actual_database == expected_database, (
            f"Expected database '{expected_database}', "
            f"but connected to '{actual_database}'."
        )

        assert mysql_version is not None

        print(f"MySQL database: {actual_database}")
        print(f"MySQL version: {mysql_version}")

    finally:
        database.disconnect()


@pytest.mark.smoke
@pytest.mark.database
@pytest.mark.oracle
def test_oracle_database_connection() -> None:
    """Verify that the Oracle source database is accessible."""

    database = OracleDatabase()
    connection = database.connect()
    oracle_config = ConfigReader().get_oracle_config()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                USER,
                SYS_CONTEXT('USERENV', 'DB_NAME'),
                SYS_CONTEXT('USERENV', 'INSTANCE_NAME')
            FROM dual
            """
        )

        result = cursor.fetchone()
        cursor.close()

        assert result is not None, (
            "Oracle connection query returned no result."
        )

        actual_user, database_name, instance_name = result

        assert actual_user.upper() == (
            oracle_config["user"].upper()
        ), (
            f"Expected Oracle user "
            f"'{oracle_config['user']}', "
            f"but connected as '{actual_user}'."
        )

        assert database_name is not None
        assert instance_name is not None

        print(f"Oracle user: {actual_user}")
        print(f"Oracle database: {database_name}")
        print(f"Oracle instance: {instance_name}")

    finally:
        database.disconnect()