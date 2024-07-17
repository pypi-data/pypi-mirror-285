from pathlib import Path
import shutil
import logging


class Ascii_File:
    EXTENSION = ".asc"
    BASE_PATH = Path(r"\\server\ascii")
    RENAMED_SUFFIX = "_OLD"
    ROOT_DIR_SUFFIX = "ASCII"
    FILE_NUMBER_LENGTH = 8

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_extension = self.file_path.suffix
        self.stem = self.file_path.stem
        logging.info(f"Processing file: {self.stem}")
        if (
            len(self.stem) < self.FILE_NUMBER_LENGTH
            or self.file_extension.lower() != self.EXTENSION
        ):
            raise ValueError(f"Invalid file: {self.stem}")
        self.name = self.stem[:8]
        self.year = self.name[:2]
        self.month = self.name[2:4]
        self.number = self.name[4:8]
        self.root_dir = self.BASE_PATH / f"{self.year}{self.ROOT_DIR_SUFFIX}"
        self.file_destination_dir = self.root_dir / self.month
        self.final_file_path = (
            self.file_destination_dir / f"{self.name}{self.EXTENSION}"
        )

    def relocate_safely(self) -> None:
        if not Path.exists(self.file_destination_dir):
            Path.mkdir(self.file_destination_dir, parents=True, exist_ok=True)

        if Path.exists(self.final_file_path):
            self.rename_old_files()

        shutil.move(self.file_path, self.final_file_path)

    def rename_old_files(self, new_file_path: Path | None = None) -> None:
        if not new_file_path:
            new_file_path = Path(
                str(self.final_file_path).replace(
                    self.EXTENSION, f"{self.RENAMED_SUFFIX}{self.EXTENSION}"
                )
            )
        try:
            Path.rename(self.final_file_path, new_file_path)
            logging.info(f"File renamed to: {new_file_path}")
            return
        except Exception:
            logging.info(
                f"File already exists: {new_file_path}. Trying again..."
            )
            new_file_path = Path(
                str(new_file_path).replace(
                    self.EXTENSION, f"{self.RENAMED_SUFFIX}{self.EXTENSION}"
                )
            )

        self.rename_old_files(new_file_path)
