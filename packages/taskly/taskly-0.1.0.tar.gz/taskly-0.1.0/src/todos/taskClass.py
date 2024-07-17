from _utils import console

class Task(object):
    """
    Task object.

    Contains:
    title (str): The title of the task.
    description (str): The description of the task.
    """
    def __init__(self):
        self.title: str = str(console.input("[b][i]Enter title:[/b][/i] "))
        while self.title == "":
            self.title = str(console.input("[b][i]Enter title:[/b][/i] "))
        self.description: str = str(console.input("[b][i]Enter description:[/b][/i] "))
        print()