import sqlite3
from utility import Utility
from typing import Literal
import uuid


class Tools:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
        self.utility = Utility()

    def search_patient( self, first_name: str, last_name: str, dob: str ) -> dict:

        if not self.utility.validate_dob(dob):
            return {
                "status": False,
                "message": "Invalid DOB format. Use YYYY-MM-DD"
            }

        query = '''
            SELECT patient_id FROM patient
            WHERE first_name = ? AND last_name = ? AND dob = ?
        '''

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

    def insert_patient( self, first_name: str, last_name: str, dob: str, gender: Literal["Male", "Female"],
                        phone: str, email: str, insurance_company: str, member_id: str, group_id: str ) -> dict:

        if not self.utility.validate_dob(dob):
            return {
                "status": False,
                "message": "Incorrect Date of Birth"
            }

        if not self.utility.validate_email(email):
            return {
                "status": False,
                "message": "Incorrect Email"
            }

        if not phone.isdigit():
            return {
                "status": False,
                "message": "Phone number must contain only digits"
            }

        if len(phone) != 10:
            return {
                "status": False,
                "message": "Phone number should have exactly 10 digits"
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

        query = '''
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
        '''

        try:
            patient_id = str(uuid.uuid4())

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

    def doctor_availibility( self, day_of_week: Literal[
                                "Sunday", "Monday", "Tuesday",
                                "Wednesday", "Thursday", "Friday", "Saturday"],
                            time_slot: str, duration: Literal[15, 30],
                            speciality: Literal[
                                "Cardiology", "Dermatology", "Orthopedics",
                                "Neurology", "Pediatrics", "ENT"]
                            ) -> dict:

        day_mapping = { "Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4, "Thursday": 5,
            "Friday": 6, "Saturday": 7 }

        day_num = day_mapping[day_of_week]

        try:
            query = '''
                SELECT * FROM doctor_schedule
                WHERE speciality = ?
                AND day_of_week = ?
                AND time_slot = ?
                AND is_booked = 0
            '''

            self.cursor.execute(
                query,
                (speciality, day_num, time_slot)
            )

            slot = self.cursor.fetchone()

            if slot:
                return {
                    "status": True,
                    "message": "Exact slot available",
                    "data": slot
                }

            query = '''
                SELECT * FROM doctor_schedule
                WHERE speciality = ?
                AND day_of_week = ?
                AND is_booked = 0
                ORDER BY time_slot
            '''

            self.cursor.execute(
                query,
                (speciality, day_num)
            )

            alternate_same_day = self.cursor.fetchall()

            if alternate_same_day:
                return {
                    "status": True,
                    "message": "Requested slot unavailable. Alternate slots available on same day",
                    "data": alternate_same_day
                }

            query = '''
                SELECT * FROM doctor_schedule
                WHERE speciality = ?
                AND is_booked = 0
                ORDER BY day_of_week, time_slot
            '''

            self.cursor.execute(
                query,
                (speciality,)
            )

            alternate_other_days = self.cursor.fetchall()

            if alternate_other_days:
                return {
                    "status": True,
                    "message": "No slots on requested day. Alternate slots available on different days",
                    "data": alternate_other_days
                }

            return {
                "status": False,
                "message": "There are no available time slots. Please check later."
            }

        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }

    def book_appointment(self, schedule_id: str) -> dict:

        check_query = '''
            SELECT is_booked
            FROM doctor_schedule
            WHERE schedule_id = ?
        '''

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
                    "message": "This slot is already booked"
                }

            query = '''
                UPDATE doctor_schedule
                SET is_booked = 1
                WHERE schedule_id = ?
            '''

            self.cursor.execute(query, (schedule_id,))
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
