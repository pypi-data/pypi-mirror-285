from .constants import SERVER_DIRECTORY
from pathlib import Path


class DestinationPathGenerator:
    FILE_DIR_MAP = {
        "COGO": ["cogo", "COGO", "{year}COGO", "{month}"],
        "ASCII": ["ascii", "{year}ASCII", "{month}"],
        "DWG": ["dwg", "{year}dwg", "{month}"],
    }

    def __init__(self, root_dir: Path = SERVER_DIRECTORY) -> None:
        self.root_dir = root_dir

    def get_file_destination_directory(
        self, file_type: str, **kwargs: str
    ) -> Path:
        file_directory = self.FILE_DIR_MAP.get(file_type)
        if not file_directory:
            raise ValueError(f"Invalid file type: {file_type}")

        file_directory = [part.format(**kwargs) for part in file_directory]

        file_destination_directory = self.root_dir / Path(*file_directory)

        return file_destination_directory
