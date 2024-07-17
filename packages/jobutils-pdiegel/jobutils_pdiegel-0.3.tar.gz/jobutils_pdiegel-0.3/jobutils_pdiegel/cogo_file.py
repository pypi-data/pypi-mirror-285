from pathlib import Path


class CogoFile:
    NUM_COLUMNS_PER_LINE = 4

    def __init__(self, cogo_file: Path) -> None:
        self.cogo_file = cogo_file

    def convert_to_ascii(self, destination: Path) -> None:
        if not self.file_exists():
            self.fix_file_extension()
        with open(self.cogo_file, "r") as cogo_file:
            with open(destination, "w") as ascii_file:
                point_number = 0
                for line in cogo_file:
                    if not self.is_valid_line(line):
                        print(f"Invalid line: {line}")
                        continue
                    point_number += 1

                    columns = self.parse_cogo_line(line)
                    northing, easting, elevation, description = columns

                    elevation = self.format_elevation(elevation)

                    ascii_line = ",".join(
                        [
                            str(point_number),
                            northing,
                            easting,
                            elevation,
                            description,
                        ]
                    )

                    ascii_file.write(ascii_line + "\n")

    def is_valid_line(self, line: str) -> bool:
        columns = self.parse_cogo_line(line)

        if not self.has_valid_columns(columns):
            return False

        northing, easting, _, _ = columns
        if not self.has_valid_coordinates(northing, easting):
            return False

        return True

    def has_valid_columns(self, columns: list[str]) -> bool:
        return len(columns) == self.NUM_COLUMNS_PER_LINE

    def has_valid_coordinates(self, northing: str, easting: str) -> bool:
        return int(float(northing)) + int(float(easting)) != 0

    def parse_cogo_line(self, line: str) -> list[str]:
        return [value.strip() for value in line.split(",")]

    def format_elevation(self, elevation: str) -> str:
        if not elevation.isnumeric():
            return "0"
        # Elevations are in feet, so large negative values are invalid
        elif int(elevation) < -5:
            return "0"
        return elevation

    def file_exists(self) -> bool:
        return self.cogo_file.exists()

    def fix_file_extension(self) -> None:
        if self.cogo_file.suffix != ".cgf":
            self.cogo_file.rename(self.cogo_file.with_suffix(".cgf"))
