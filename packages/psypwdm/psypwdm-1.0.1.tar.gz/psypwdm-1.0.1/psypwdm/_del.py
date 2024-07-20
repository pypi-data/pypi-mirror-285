from ._connect import Connection

def delete() -> None:
    """Delete passwordmanager table from database
    
    """
    conn = Connection()
    query_string = f"DROP TABLE IF EXISTS passwordmanager"
    user_in = input("Are you sure you want to delete the passwordmanager table and contents? [Y/N]")
    if user_in.lower() == 'y':
        conn.cursor.execute(query_string)
        conn.commit()
        print('the passwordmanager table has been deleted.')

    conn.close()