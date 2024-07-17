import os

from _utils import *

from ._todo import todo
from .maindb import *


@caution()
def app():
    """
    The main function of the application. It handles user interactions, database management, and task management.

    Returns:
        False (0): for ending the program  
    """
    
    settings: dict = Settings.get_data()['settings']

    db_file: str = os.path.expanduser(f"{Settings.get_data()["settings"]["database_dir"]}{Settings.get_data()["settings"]["main_db"]}.db")

    # Ensure the directory exists
    db_dir: str = os.path.dirname(db_file)
    os.makedirs(db_dir, exist_ok=True)
    
    cursor, conn = db_connect(db_file)
    
    # Fetch all databases from the database
    databases = db_query(cursor)
    
    # Display the list of databases and ask user for choice
    if len(databases) != 0:    
        printList(databases)
        console.print("Enter 'n' for new database\nEnter 'd' for deleting a database\nEnter '0' to end program\nEnter id for opening a database\nEnter Choice: ", style="bold italic Blue", end="")
        choice: str = input()
    else:
        choice = 'n'

    # select action based on choice
    
    # add db
    if choice == 'n':
        db_add(cursor, conn)
        
    # delete db
    elif choice == 'd':
        db_delete(cursor, conn, databases)

    # ! don't remove this, necessary for exiting the program and also for the correct functionality of the program
    elif choice == '0':
        console.print("Exiting...", style="red bold")
        cursor.close()
        conn.close()
        return 0
    
    # clear terminal
    elif choice == 'clear':
        clear_terminal()
    
    # prevent negative index
    elif '-' in choice:
        raise ValueError
    
    # open a db
    else:
        cursor.close()
        conn.close()
        # // print(databases)
        try:
            # ! When 0 is entered the the index become -1 which refers to the last item in the database list.
            todo(databases[int(choice)-1][0])
        except IndexError:
            console.print("Invalid ID", style="red bold")


if __name__ == "__main__":
    app()
