import sqlite3

from _utils import *


@caution()
def db_connect(file: str):
    """connects to the main database where list of task databases is stored

    Args:
        file (str): name of the database to connect to

    Returns:
        sqlite3 objects: cursor object and connector object
    """

    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks_list (
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """
    )

    return cursor, conn


@caution()
def db_query(cursor):
    """queries main database

    Args:
        cursor (sqlite3 object): cursor

    Returns:
        list of tuple ('name', 'description')
    """

    cursor.execute("Select * FROM tasks_list")
    data: list[tuple[str, str]] = cursor.fetchall()
    return data


@caution()
def db_add(cursor, conn):
    """add data to the database

    Args:
        cursor (sqlite3 object): cursor
        conn (sqlite3 object): connection
    """

    console.print("\nAdding a new Database\n", style="bold green", justify="center")
    name: str = console.input(("[b][i]Enter Name: [/i][/b] "))
    while name == "":
        name = console.input(("[b][i]Enter Name: [/i][/b] "))
    description: str = console.input(("[b][i]Enter Description: [/i][/b]"))
    try:
        cursor.execute(
            """
            INSERT INTO tasks_list (name, description)
            VALUES (?, ?)
        """,
            (name, description),
        )
        console.print("Database was added", style="green bold")
        conn.commit()
    except sqlite3.IntegrityError:
        console.print("Task with the same Name already exists.", style="red, bold")


@caution()
def db_delete(cursor, conn, tasks):
    """deletes data from the database

    Args:
        cursor (sqlite3 object): cursor
        conn (sqlite3 object): connection
    """

    printList(tasks)
    id: int = int(console.input("[b][i]Enter ID: [/i][/b] ")) - 1
    dir = Settings.get_data()
    dir = Settings.get_data()["settings"]["database_dir"]
    name: str = tasks[id][0]
    path: str = f"{dir}{name}.db"
    delete_file(path)
    cursor.execute(
        """
        DELETE FROM tasks_list
        WHERE name = ?               
    """,
        (tasks[id][0],),
    )
    conn.commit()
    console.print("Database was deleted", style="red bold")
