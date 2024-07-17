import os
import platform
import time

from ._rich import console


def wait_for_enter():
    """Waits for Enter key press"""
    input("Press Enter to continue...")


def clear_terminal():
    """Clears the terminal"""

    current_os = platform.system()
    if current_os == "Windows":
        os.system("cls")
        print()
    else:  # Linux and MacOS
        os.system("clear")
        print()


def caution(msg: str = "An error occurred", sleep_time: int = 1):
    """
    decorator function for warning messages

    Args:
        msg (str): msg to be displayed. Defaults to "An error occurred".
        sleep_time (int): time sleep Defaults to 1.
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                console.print(msg, style="red bold blink")
                time.sleep(sleep_time)

        return wrapper

    return decorator


def delete_file(filepath: str):
    """helper function to delete a file

    Args:
        filepath (_type_): path to the file
    """

    # Expand user directory symbol ~ to full path
    full_path = os.path.expanduser(filepath)

    # Check if the file exists
    if os.path.exists(full_path):
        os.remove(full_path)
    else:
        pass
