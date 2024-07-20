from ._connect import Connection
from getpass import getpass
from datetime import datetime as dt

import hashlib
import bcrypt

def _insert_query(**kwargs) -> None:
    """generic query insertion into database

    Parameters
    ----------
    kwargs : dict
        kwargs.keys() are the name of the fields in which to insert values
        kwargs.values() are the values of the fields to be inserted       

    """
    conn = Connection() # connection to database is open
    query_string = "INSERT INTO passwordmanager" + f"({', '.join([str(k) for k in kwargs.keys()])}) VALUES \
        ({', '.join(['%s' for _ in range(len(kwargs))])})"
    insert_values = [f'{v}' for v in kwargs.values()]
    conn.cursor.execute(f"""{query_string}""", insert_values)
    conn.commit()
    conn.close()

def insert(useraccountsystemtype: str, username: str, comments: str) -> None:
    """insert new entry into the password manager database
    
    Parameters
    ----------
    useraccountsystemtype : str
        the system hosting user's content and data, e.g., 'bank account', 'email', etc.

    username : str
        the name to access the account
    
    comments : str
        any comments about the entry to give it context, e.g., password hint, if current entry is an update such as 
        a password change, etc. 

    """
    timestamp = dt.now()
    salt = bcrypt.gensalt().decode('utf-8')
    password = hashlib.sha256(getpass("insert password: ").encode('utf-8') + salt.encode('utf-8')).hexdigest()
    
    # # check if entry with above values exist in database
    # conn = Connection() # connection is open
    # query_string = f"SELECT * FROM passwordmanager WHERE \
    #     timestamp = '{timestamp}' AND \
    #     useraccountsystemtype = '{useraccountsystemtype}' AND \
    #     username = '{username}' AND \
    #     password = '{password}' AND \
    #     salt = '{salt}' AND \
    #     comments = '{comments}' \
    #     "
    # conn.cursor.execute(f"""{query_string}""")

    # rsults = conn.cursor.fetchall()
    # conn.commit()   
    # conn.close()

    _insert_query(
        timestamp=timestamp,
        useraccountsystemtype=useraccountsystemtype,
        username=username,
        password=password,
        salt=salt,
        comments=comments 
        )
    print("entry successfully added to passwordmanager!")
        