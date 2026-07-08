import sqlite3
import uuid
from typing import Literal
from langchain.tools import tool
from utility import Utility
from generate_email import send_email


class Tools:
    def __init__(self):
        self.db_path = "database.db"
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (first_name, last_name, dob))
                patient = cursor.fetchone()

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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
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
                conn.commit()

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

    def get_available_doctors(self, day_of_week : Literal[
        "Sunday", "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday"
    ], speciality: Literal[
        "Cardiology",
        "Dermatology",
        "Orthopedics",
        "Neurology",
        "Pediatrics",
        "ENT"
    ]) -> dict:
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
        SELECT schedule_id, doctor_name, speciality, time_slot
        FROM doctor_schedule
        WHERE speciality = ?
        AND day_of_week = ?
        AND is_booked = 0
        ORDER BY time_slot ASC
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (speciality, day_num))
                slots = cursor.fetchall()

            if not slots:
                return {
                    "status": False,
                    "message": "No available slots for the given day and speciality"
                }
            
            return {
                "status": True,
                "message": "Available slots retrieved successfully",
                "data": [
                    {
                        "schedule_id": slot[0],
                        "doctor_name": slot[1],
                        "speciality": slot[2],
                        "time_slot": slot[3]
                    }
                    for slot in slots
                ]
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
        duration: Literal[15, 30],
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
        SELECT schedule_id, doctor_name, speciality, day_of_week, time_slot
        FROM doctor_schedule
        WHERE speciality = ?
        AND day_of_week = ?
        AND time_slot = ?
        AND is_booked = 0
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query,
                    (speciality, day_num, time_slot)
                )
                slot = cursor.fetchone()

            if slot:
                return {
                    "status": True,
                    "message": f"{duration} minute slot available",
                    "data": {
                        "schedule_id": slot[0],
                        "doctor_name": slot[1],
                        "speciality": slot[2],
                        "day_of_week": slot[3],
                        "time_slot": slot[4]
                    }
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

        update_query = """
        UPDATE doctor_schedule
        SET is_booked = 1
        WHERE schedule_id = ?
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(check_query, (schedule_id,))
                slot = cursor.fetchone()

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

                cursor.execute(update_query, (schedule_id,))
                conn.commit()

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


# Tool wrappers

@tool
def search_patient_tool(
    first_name: str,
    last_name: str,
    dob: str
):
    """Search whether a patient already exists in the system.

    Call this FIRST before any registration or booking.
    Returns patient_id if found, or status=False if not found.

    Args:
        first_name: Patient's first name (case-sensitive)
        last_name: Patient's last name (case-sensitive)
        dob: Date of birth in YYYY-MM-DD format
    """
    db = Tools()
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
    """Register a new patient in the system.

    Only call this after search_patient_tool confirms the patient does NOT exist.
    All fields are required. Returns patient_id on success.

    Args:
        first_name: Patient's first name
        last_name: Patient's last name
        dob: Date of birth in YYYY-MM-DD format
        gender: Must be exactly 'Male' or 'Female'
        phone: Exactly 10 digits, no spaces or dashes
        email: Valid email address
        insurance_company: Name of insurance provider
        member_id: Insurance member ID
        group_id: Insurance group ID
    """
    db = Tools()
    return db.insert_patient(
        first_name, last_name, dob, gender,
        phone, email, insurance_company, member_id, group_id
    )


@tool
def doctor_availability_tool(
    day_of_week: str,
    time_slot: str,
    duration: int,
    speciality: str
):
    """Check if a doctor slot is available for a given specialty, day, and time.

    ALWAYS call this tool to check availability. Never assume a slot is
    unavailable without calling this. If the slot is taken, ask the user
    for a different day or time and call this tool again.

    Returns schedule_id on success — pass this directly to book_appointment_tool.

    Args:
        day_of_week: Full day name e.g. 'Monday', 'Tuesday', 'Wednesday'
        time_slot: Time in HH:MM 24-hour format e.g. '10:00', '14:30'
        duration: 15 for existing patients, 30 for newly registered patients
        speciality: One of: Cardiology, Dermatology, Orthopedics,
                    Neurology, Pediatrics, ENT
    """
    db = Tools()
    return db.doctor_availability(day_of_week, time_slot, duration, speciality)


@tool
def book_appointment_tool(schedule_id: str):
    """Book a confirmed available appointment slot.

    Only call this after doctor_availability_tool returns a valid schedule_id
    AND the user has confirmed they want to proceed.
    Marks the slot as booked — this cannot be undone.

    Args:
        schedule_id: The schedule_id returned by doctor_availability_tool
    """
    db = Tools()
    return db.book_appointment(schedule_id)

@tool
def get_available_slots_tool(
    day_of_week: str,
    speciality: str
):
    """Get all available time slots for a given day and specialty.
 
    Call this when the user has NOT specified an exact time, or says
    something vague like 'Wednesday morning' or 'any time Thursday'.
    Returns a list of available slots so the user can choose one.
    Once the user picks a time, use doctor_availability_tool to confirm
    and get the schedule_id for booking.
 
    Args:
        day_of_week: Full day name e.g. 'Monday', 'Wednesday'
        speciality: One of: Cardiology, Dermatology, Orthopedics,
                    Neurology, Pediatrics, ENT
    """
    db = Tools()
    return db.get_available_doctors(day_of_week, speciality)

@tool
def send_email_tool(
    subject: str,
    sender: str,
    receiver: str,
    body: str
):
    """Create a dummy email for confirmation of doctor appoitment.

    Args:
        subject: Subject line of the email
        sender: Sender's email address
        receiver: Receiver's email address
        body: Body content of the email
    """
    try:
        send_email(subject, sender, receiver, body)
        return {
            "status": True,
            "message": "Email sent successfully"
        }
    except Exception as e:
        return {
            "status": False,
            "message": f"Failed to send email: {e}"
        }




TOOLS = [
    search_patient_tool,
    insert_patient_tool,
    doctor_availability_tool,
    get_available_slots_tool,
    book_appointment_tool,
    send_email_tool,
]