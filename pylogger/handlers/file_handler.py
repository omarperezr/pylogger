from datetime import datetime
from pathlib import Path


class FileHandler:
    """A custom loguru handler that writes logs to a file. It takes a log folder and a file name as input
    and writes the logs to the specified file in the specified folder. The write method is used to write the logs to the
    file.

    Attributes:
        log_folder: str
            The folder where the log file will be stored.
        file_name: str
            The name of the log file. Defaults to the current date in YYYY-MM-DD format.

    Example:
        file_handler = FileHandler("logs")
        logger.add(file_handler)
    """

    def __init__(self, log_folder, file_name=f"{datetime.now().date()}.log"):
        self.log_folder = log_folder
        self.file_name = file_name

    def write(self, message):
        with open(Path(self.log_folder).joinpath(self.file_name), "a") as f:
            f.write(message + "\n")


file_handler = FileHandler("logs")
