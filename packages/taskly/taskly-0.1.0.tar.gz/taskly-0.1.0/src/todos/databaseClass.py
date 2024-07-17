import sqlite3
import os
from .taskClass import Task
from _utils import Settings


class Database:
    """
    Initialize a new instance of the Database class.

    This class creates a connection to a SQLite database file located in the user's home directory.
    The database file is named after the provided 'name' parameter. If the directory does not exist,
    it is created. The database contains a 'tasks' table with columns for 'id', 'title', 'description',
    and 'completed'.

    Parameters:
    name (str): The name of the database file and the tasks table.

    Returns:
    None
    """

    def __init__(self, name):
        db_file = os.path.expanduser(f"{Settings.get_data()["settings"]["database_dir"]}{name}.db")

        # Ensure the directory exists
        db_dir = os.path.dirname(db_file)
        os.makedirs(db_dir, exist_ok=True)

        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                description TEXT,
                completed INTEGER DEFAULT 0
            )
        """
        )

    def add_task(self, task):
        """
        Add a new task to the tasks table in the database.

        This method attempts to insert a new task into the 'tasks' table. If a task with the same title
        already exists in the table, an IntegrityError is raised and a message is printed to the console.
        After the insertion, the changes are committed to the database.

        Parameters:
        task (TaskClass): An instance of the TaskClass representing the task to be added. The task's
                        title and description attributes are used for the insertion.

        Returns:
        None
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO tasks (title, description)
                VALUES (?, ?)
            """,
                (task.title, task.description),
            )
        except sqlite3.IntegrityError:
            print("Task with the same title already exists.")
        self.conn.commit()

    def remove_task(self, identifier):
        """
        Remove a task from the tasks table in the database based on the provided identifier.

        This method deletes a task from the 'tasks' table in the database using the provided 'identifier'.
        The 'identifier' parameter should correspond to the 'id' column of the task to be removed. After the
        deletion, the changes are committed to the database.

        Parameters:
        identifier (int): The unique identifier of the task to be removed. This corresponds to the 'id'
                        column in the 'tasks' table.

        Returns:
        None
        """
        self.cursor.execute(
            """
            DELETE FROM tasks
            WHERE id = ?
        """,
            (identifier,),
        )
        self.conn.commit()

    def update_description(self, identifier, description=None):
        """
        Update the description of a task in the tasks table based on the provided identifier.

        This method updates the 'description' column of a task in the 'tasks' table in the database.
        The task is identified by the provided 'identifier', which corresponds to the 'id' column in the
        'tasks' table. If the 'description' parameter is not provided, the 'description' column is set to
        NULL. After the update, the changes are committed to the database.

        Parameters:
        identifier (int): The unique identifier of the task to be updated. This corresponds to the 'id'
                        column in the 'tasks' table.
        description (str, optional): The new description for the task. If not provided, the 'description'
                                    column is set to NULL.

        Returns:
        None
        """
        self.cursor.execute(
            """
            UPDATE tasks
            SET description = ?
            WHERE id = ?
        """,
            (description, identifier),
        )
        self.conn.commit()

    def update_completed(self, identifier):
        """
        Update the completion status of a task in the tasks table based on the provided identifier.

        This method updates the 'completed' column of a task in the 'tasks' table in the database.
        The task is identified by the provided 'identifier', which corresponds to the 'id' column in the
        'tasks' table. The 'completed' column is set to 1, indicating that the task is completed.
        After the update, the changes are committed to the database.

        Parameters:
        identifier (int): The unique identifier of the task to be updated. This corresponds to the 'id'
                        column in the 'tasks' table.

        Returns:
        None
        """
        self.cursor.execute(
            """
            UPDATE tasks
            SET completed = 1
            WHERE id = ?
        """,
            (identifier,),
        )
        self.conn.commit()

    def query(self):
        """
        Retrieve all tasks from the tasks table in the database.

        This method executes a SELECT query on the 'tasks' table in the database.
        It retrieves all columns for all tasks and returns them as a list of tuples.

        Parameters:
        None

        Returns:
        rows (list): A list of tuples, where each tuple represents a row from the 'tasks' table.
                    Each tuple contains the following elements:
                    - id (int): The unique identifier of the task.
                    - title (str): The title of the task.
                    - description (str): The description of the task.
                    - completed (int): A flag indicating whether the task is completed (1) or not (0).
        """
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        return rows

    def exit(self):
        """
        Close the database connection and cursor.

        This method closes the SQLite database connection and cursor associated with the instance.
        It should be called when the instance is no longer needed to free up system resources.

        Parameters:
        None

        Returns:
        None
        """
        self.cursor.close()
        self.conn.close()


# Example usage
if __name__ == "__main__":
    db = Database("mytodos")
    # Use the database methods here...
    db.exit()
