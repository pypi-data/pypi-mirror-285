from ._connect import Connection
from getpass import getpass
import hashlib

def retrieve(**kwargs) -> list:
    """run query to retrieve entry from database
    
    Parameters
    ----------
    kwargs : dict, optional
        pass field names as kwargs.keys with values as kwargs.values to retrieve.
        If left blank, retrieve all entries and print to console
    
    Returns
    -------
    results : list
        a list of results obtained from the database through executing the query

    """
    conn = Connection()
    if len(kwargs) == 0:
        query_string = "SELECT * FROM passwordmanager"
    else:
        query_string = f"""SELECT * FROM passwordmanager WHERE {"AND ".join([f"{k} = '{v}'" for k, v in kwargs.items()])}"""
    conn.cursor.execute(f"""{query_string}""")
    conn.commit()
    rsults = conn.cursor.fetchall()
    conn.close()
    return rsults

def retrieve_for_pwd() -> list:
    """Retrieve entries based on matching password hash

    Returns
    -------
    results : list
        a list of entries in the database with matching password hash

    """
    conn = Connection()
    password = getpass('insert password: ')
    hashpass = lambda x: hashlib.sha256(password.encode('utf-8') + x.strip().encode('utf-8')).hexdigest()

    query_string = "SELECT id, password, salt FROM passwordmanager"
    conn.cursor.execute(f"""{query_string}""")
    rsults = conn.cursor.fetchall()
    ids = []
    for rsult in rsults:
        identifier = rsult[0]
        pwd = rsult[1]
        salt = rsult[-1]
        try:
            hashed = hashpass(salt)
        except AttributeError:
            hashed = hashpass('')

        if hashed == pwd:
            ids += [identifier]

    conn.close()
    if len(ids) == 0:
        return []
    else:
        conn = Connection()
        query_string = f"SELECT * FROM passwordmanager WHERE id IN ({', '.join([str(i) for i in ids])})"
        conn.cursor.execute(f"""{query_string}""")
        rsults = conn.cursor.fetchall()
        conn.close()
        return rsults
