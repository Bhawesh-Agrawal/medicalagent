import sqlite3
import uuid
from typing import Literal
from langchain.tools import tool
from utility import Utility


class Tools:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
        self.utility = Utility()

    def search_patient(
        self,
        first_name: str,
        last_name: str,
        dob: str
    ) -> dict:
        """Search if patient exists."""

        if not self.utility.validate_dob(dob):
            return {
                "status": False,
                "message": "Invalid DOB format. Use YYYY-MM-DD"
            }

        query = """
        SELECT patient_id
        FROM patient
        WHERE first_name = ? AND last_name = ? AND dob = ?
        """

        try:
            self.cursor.execute(query, (first_name, last_name, dob))
            patient = self.cursor.fetchone()

            if patient:
                return {
                    "status": True,
                    "message": "Patient found",
                    "data": {
                        "patient_id": patient[0]
                    }
                }

            return {
                "status": False,
                "message": "Patient not found"
            }

        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }

    def insert_patient(
        self,
        first_name: str,
        last_name: str,
        dob: str,
        gender: Literal["Male", "Female"],
        phone: str,
        email: str,
        insurance_company: str,
        member_id: str,
        group_id: str
    ) -> dict:
        """Insert new patient."""

        if not self.utility.validate_dob(dob):
            return {
                "status": False,
                "message": "Invalid DOB format"
            }

        if not self.utility.validate_email(email):
            return {
                "status": False,
                "message": "Invalid email"
            }

        if not phone.isdigit() or len(phone) != 10:
            return {
                "status": False,
                "message": "Phone number must be exactly 10 digits"
            }

        existing_patient = self.search_patient(
            first_name,
            last_name,
            dob
        )

        if existing_patient["status"]:
            return {
                "status": False,
                "message": "Patient already exists"
            }

        patient_id = str(uuid.uuid4())

        query = """
        INSERT INTO patient (
            patient_id,
            first_name,
            last_name,
            dob,
            gender,
            phone,
            email,
            insurance_company,
            member_id,
            group_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            self.cursor.execute(
                query,
                (
                    patient_id,
                    first_name,
                    last_name,
                    dob,
                    gender,
                    phone,
                    email,
                    insurance_company,
                    member_id,
                    group_id
                )
            )

            self.conn.commit()

            return {
                "status": True,
                "message": "Patient inserted successfully",
                "data": {
                    "patient_id": patient_id
                }
            }

        except sqlite3.IntegrityError:
            return {
                "status": False,
                "message": "Email already exists"
            }

        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }

    def doctor_availability(
        self,
        day_of_week: Literal[
            "Sunday", "Monday", "Tuesday",
            "Wednesday", "Thursday", "Friday", "Saturday"
        ],
        time_slot: str,
        speciality: Literal[
            "Cardiology",
            "Dermatology",
            "Orthopedics",
            "Neurology",
            "Pediatrics",
            "ENT"
        ]
    ) -> dict:
        """Check doctor availability."""

        day_mapping = {
            "Sunday": 1,
            "Monday": 2,
            "Tuesday": 3,
            "Wednesday": 4,
            "Thursday": 5,
            "Friday": 6,
            "Saturday": 7
        }

        day_num = day_mapping[day_of_week]

        query = """
        SELECT *
        FROM doctor_schedule
        WHERE speciality = ?
        AND day_of_week = ?
        AND time_slot = ?
        AND is_booked = 0
        """

        try:
            self.cursor.execute(
                query,
                (speciality, day_num, time_slot)
            )

            slot = self.cursor.fetchone()

            if slot:
                return {
                    "status": True,
                    "message": "Slot available",
                    "data": slot
                }

            return {
                "status": False,
                "message": "Requested slot unavailable"
            }

        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }

    def book_appointment(
        self,
        schedule_id: str
    ) -> dict:
        """Book appointment."""

        check_query = """
        SELECT is_booked
        FROM doctor_schedule
        WHERE schedule_id = ?
        """

        try:
            self.cursor.execute(check_query, (schedule_id,))
            slot = self.cursor.fetchone()

            if not slot:
                return {
                    "status": False,
                    "message": "Invalid schedule ID"
                }

            if slot[0] == 1:
                return {
                    "status": False,
                    "message": "Slot already booked"
                }

            update_query = """
            UPDATE doctor_schedule
            SET is_booked = 1
            WHERE schedule_id = ?
            """

            self.cursor.execute(update_query, (schedule_id,))
            self.conn.commit()

            return {
                "status": True,
                "message": "Appointment confirmed",
                "schedule_id": schedule_id
            }

        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }


db = Tools()


@tool
def search_patient_tool(
    first_name: str,
    last_name: str,
    dob: str
):
    """Search patient by name and DOB."""
    return db.search_patient(first_name, last_name, dob)


@tool
def insert_patient_tool(
    first_name: str,
    last_name: str,
    dob: str,
    gender: str,
    phone: str,
    email: str,
    insurance_company: str,
    member_id: str,
    group_id: str
):
    """Insert new patient."""
    return db.insert_patient(
        first_name,
        last_name,
        dob,
        gender,
        phone,
        email,
        insurance_company,
        member_id,
        group_id
    )


@tool
def doctor_availability_tool(
    day_of_week: str,
    time_slot: str,
    speciality: str
):
    """Check doctor availability."""
    return db.doctor_availability(
        day_of_week,
        time_slot,
        speciality
    )


@tool
def book_appointment_tool(
    schedule_id: str
):
    """Book doctor appointment."""
    return db.book_appointment(schedule_id)


TOOLS = [
    search_patient_tool,
    insert_patient_tool,
    doctor_availability_tool,
    book_appointment_tool
]