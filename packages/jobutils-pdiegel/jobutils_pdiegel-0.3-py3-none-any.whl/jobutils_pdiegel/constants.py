from pathlib import Path
from datetime import datetime
import dotenv
import os

SERVER_DIRECTORY = Path("//server")

# Only need the last two digits of the year
CURRENT_YEAR = int(str(datetime.now().year)[2:])


OLD_JOB_YEAR_RANGE = [str(year) for year in range(90, 99 + 1)]  # 1900-1999

new_job_year_range = range(0, CURRENT_YEAR + 1)  # 2000-CURRENT_YEAR
# Have to add leading zeroes to single digit years to match our numbering system
NEW_JOB_YEAR_RANGE = [f"{year:02}" for year in new_job_year_range]

JOB_YEAR_RANGE = OLD_JOB_YEAR_RANGE[:]
JOB_YEAR_RANGE.extend(NEW_JOB_YEAR_RANGE)

FILE_TYPE_MAP = {
    ".cgf": "COGO",
    ".asc": "ASCII",
    ".dwg": "DWG",
}

dotenv.load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")
