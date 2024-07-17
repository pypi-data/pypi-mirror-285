import os
import shutil


class DataFile:
    """
    Data File class for configurations

    Args:
        path (str): The path to the configuration file
        default_path (str): The path to the default settings file

    Methods:
        get_data: Get the configuration data
    """

    def __init__(self, path: str, default_path: str):

        # Define the path to the local default settings file
        self.default_file = os.path.join(os.path.dirname(__file__), default_path)

        # Define the path to the configuration file
        self.file_path = os.path.expanduser(path)

    def get_data(self) -> dict:
        """get data from the configuration file

        Returns:
            data: dictionary of configuration
        """
        if not os.path.exists(self.file_path):
            self.__set_default_file()

        # Load and return the configuration
        data = {}
        with open(self.file_path, "r") as f:
            exec(f.read(), data)

        return data

    def __set_default_file(self):
        """set default file configuration"""

        if not os.path.exists(self.file_path):
            self.__copy_default_settings()

    def reset_default_file(self):
        """reset the configuration file to default settings"""

        if os.path.exists(self.file_path):
            os.remove(self.file_path)

        # Copy the default settings file to self.file_path
        self.__copy_default_settings()

    def __copy_default_settings(self):
        """copy the default settings"""

        # Ensure the directory exists
        config_dir = os.path.dirname(self.file_path)
        os.makedirs(config_dir, exist_ok=True)

        # Copy the default settings file to self.file_path
        shutil.copyfile(self.default_file, self.file_path)
