from ._rich import *


def printList(list: list):
    """print list of database
    if list of tasks, then will also show the status of completion in for of emojis

    Args:
        list (list): list of tuples from databases
    """
    
    try:
        print()
        for idx, item in enumerate(list):
            console.print(f" id: [i]%2d[/i], title: [i] {item[0]}[/i], completed: {":white_heavy_check_mark:" if item[3] else ":x:"}" % (idx + 1), style="green bold" )
        print()
    except:
        print()
        for item in range(len(list)):
            console.print(f" id: [i]%2d[/i], title: [i] {list[item][0]}[/i]" % (item + 1), style="green bold" )
        print()
        
def printMenu():
    """print the menu for tasks
    """
    table = Table(title="Task Manager Menu")

    table.add_column("Option", justify="center", style="red bold", no_wrap=True)
    table.add_column("Description", style="purple")

    padding1 = (1,5,0,5)  # Padding for top, right, bottom, and left
    padding2 = (1,5,0,7)  # Padding for top, right, bottom, and left
    
    table.add_row(Padding("1", padding1), Padding("List all tasks", padding2))
    table.add_row(Padding("2", padding1), Padding("Add a task", padding2))
    table.add_row(Padding("3", padding1), Padding("Remove a task", padding2))
    table.add_row(Padding("4", padding1), Padding("Update task description", padding2))
    table.add_row(Padding("5", padding1), Padding("Mark task as completed", padding2))
    table.add_row(Padding("6", padding1), Padding("Mass remove task", padding2))
    table.add_row(Padding("7", padding1), Padding("Mass mark task as completed", padding2))
    table.add_row(Padding("0", (1,5,1,5)), Padding("Exit", (1,5,1,7)))
    print()
    console.print(table, justify="center")
    print()

def printTask(database):
    """print the tasks in the database

    Args:
        database (list): list of tuples containing ID, title, description and status of completion
    """
    tasks = database.query()
    if not tasks:
        console.print("No tasks found.", style="red bold")
        return

    padding_default = (1, 3, 0, 3)  # Default padding for top-bottom, left-right
    padding_last_row = (1, 3, 1, 3)  # Padding for the last row

    table = Table(title="Tasks")

    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Title", style="blue")
    table.add_column("Description", style="green")
    table.add_column("Status", justify="center", style="yellow")

    num_tasks = len(tasks)
    for index, task in enumerate(tasks):
        if index == num_tasks - 1:  # Check if it's the last row
            padding = padding_last_row
        else:
            padding = padding_default

        table.add_row(
            Padding(str(task[0]), padding),
            Padding(str(task[1]), padding),
            Padding(str(task[2]), padding),
            Padding(":white_heavy_check_mark:" if task[3] else ":x:", padding)
        )
    print()
    console.print(table, justify="center")
    print()
