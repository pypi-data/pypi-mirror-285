from configparser import ConfigParser
import psycopg2
import os

class Connection:
    """initialise psypwdm table in a postgres database
    
    Summary
    -------
    Arguments to initialise a connection to the local databse is stored in the `config.ini` file.
    A connection object and cursor object are stored as Connection class attributes.

    """
    def __init__(self) -> None:

        config = ConfigParser()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config.read(dir_path + '/config.ini')
        db_init = dict(config['DB_INIT'].items())

        self.connection = psycopg2.connect(**db_init)
        self.cursor = self.connection.cursor()

    def commit(self):
        connection = self.connection
        connection.commit()
        self.connection = connection

    def close(self) -> None:
        self.cursor.close()
        self.connection.close()