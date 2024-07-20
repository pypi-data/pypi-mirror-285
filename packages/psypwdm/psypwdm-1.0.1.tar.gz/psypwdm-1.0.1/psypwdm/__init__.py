from ._connect import Connection
from ._create import PasswordManagerCreate
from ._insert import insert
from ._retrieve import retrieve, retrieve_for_pwd
from ._out import out
from ._del import delete

# version
__version__ = '1.0.1'

conn = Connection()
PasswordManagerCreate(conn.cursor).create()
conn.commit()
conn.close()