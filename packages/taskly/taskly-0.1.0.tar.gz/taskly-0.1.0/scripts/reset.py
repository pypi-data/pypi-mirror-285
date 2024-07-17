import os
import shutil
import sys

# Try to import Settings from _utils._settings
try:
    from _utils._settings import Settings
except ModuleNotFoundError:
    # If import fails, adjust the Python path and try again
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
    from _utils._settings import Settings


def delete_directory(path):
    """Delete a directory and all its contents."""
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted: {path}")
    else:
        print(f"Directory not found: {path}")


def reset():
    """Delete specified directories and reset settings to default."""

    database_dir = Settings.get_data()["settings"]["database_dir"]
    # Directories to delete
    dirs_to_delete = [
        os.path.expanduser("~/.config/taskly/"),
        os.path.expanduser(database_dir),
    ]

    # Delete directories
    for directory in dirs_to_delete:
        delete_directory(directory)

    # Reset settings to default
    Settings.reset_default_file()
    print("Settings have been reset to default.")


if __name__ == "__main__":
    reset()
