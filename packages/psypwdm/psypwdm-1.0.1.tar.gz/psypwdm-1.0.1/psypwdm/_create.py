import configparser
from psycopg2.errors import DuplicateTable
import os

class PasswordManagerCreate:

    def __init__(self, cursor) -> None:
        self.cursor = cursor 

    def create(self) -> None:
        """initialise the PasswordManager table in a postgres database

        """
        cursor = self.cursor
        config = configparser.ConfigParser()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config.read(dir_path + '/config.ini')

        query_string_content = ','.join([f"{k} {v}" for k, v in config['DB_FIELDS'].items()])
        query_string: str = f"CREATE TABLE passwordmanager ({query_string_content})"
        try:
            cursor.execute(f"""{query_string}""")
            print("PasswordManager has been initialised")

        except DuplicateTable:
            pass
