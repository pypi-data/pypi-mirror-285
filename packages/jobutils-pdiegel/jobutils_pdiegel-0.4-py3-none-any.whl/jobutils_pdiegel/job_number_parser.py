from .constants import JOB_YEAR_RANGE


class JobNumberParser:
    VALID_LENGTHS = {6, 8}

    def __init__(self, job_number: str) -> None:
        self.job_number = job_number
        self.validators = [
            self.has_valid_length,
            self.has_valid_type,
            self.has_valid_year,
        ]
        self.validate_job_number()

    def validate_job_number(self) -> None:
        for validator in self.validators:
            if not validator(self.job_number):
                raise ValueError(f"Invalid job number: `{self.job_number}`")

    def has_valid_length(self, job_number: str) -> bool:
        return len(job_number) in self.VALID_LENGTHS

    def has_valid_type(self, job_number: str) -> bool:
        return job_number.isnumeric() and "-" not in job_number

    def has_valid_year(self, job_number: str) -> bool:
        return job_number[:2] in JOB_YEAR_RANGE

    def format_job_number(self) -> str:
        # Proper format is YYMNNN (6 digits) or YYMMNNNN (8 digits)
        # where Y is the year, M is the month, and N is a unique number
        # If the job number is 6 digits, it will be formatted as YY0M0NNN
        # Formatting to 8 digits for consistency throughout the program
        if len(self.job_number) == 8:
            return self.job_number

        year = self.job_number[:2]
        month = f"0{self.job_number[2]}"
        unique_number = f"0{self.job_number[3:]}"
        return f"{year}{month}{unique_number}"

    def set_job_number(self, job_number: str) -> None:
        self.job_number = job_number
        self.validate_job_number()

    @property
    def formatted_job_number(self):
        return self.format_job_number()

    @property
    def year(self):
        return self.formatted_job_number[:2]

    @property
    def month(self):
        return self.formatted_job_number[2:4]


if __name__ == "__main__":
    job_number = JobNumberParser("913137")
    print(job_number.formatted_job_number)
