from ._connect import Connection

def out(filepath: str) -> None:
    """Save passwordmanager table contents to .csv
    
    Parameters
    ----------
    filepath : str
        filepath to save passwordmanager table 
    
    """
    conn = Connection()
    copy_command: str = f"COPY passwordmanager TO STDOUT WITH CSV HEADER DELIMITER ','"
    with open(filepath, 'w') as f:
        conn.cursor.copy_expert(copy_command, f)

    print(f"Success! Contents of passwordmanager have been written to {filepath}")
    conn.close()
