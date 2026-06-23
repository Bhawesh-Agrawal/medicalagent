import re
from datetime import datetime


class Utility:

    def validate_dob(self, dob: str) -> bool:
        try:
            parsed_date = datetime.strptime(dob, "%Y-%m-%d")

            if parsed_date.date() > datetime.today().date():
                return False

            return True

        except ValueError:
            return False

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if re.match(pattern, email):
            return True

        return False