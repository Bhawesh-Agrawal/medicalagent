import sqlite3
import uuid
from typing import Literal
from langchain.tools import tool
from utility import Utility
from generate_email import send_email


DB_PATH = "database.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


class Tools:
    def __init__(self):
        self.db_path = DB_PATH
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

    def get_patient_details(self, patient_id: str) -> dict:
        """Get full patient details by patient_id."""

        query = """
        SELECT patient_id, first_name, last_name, dob, gender,
               phone, email, insurance_company, member_id, group_id
        FROM patient
        WHERE patient_id = ?
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (patient_id,))
                row = cursor.fetchone()

            if row:
                return {
                    "status": True,
                    "message": "Patient details retrieved",
                    "data": {
                        "patient_id": row[0],
                        "first_name": row[1],
                        "last_name": row[2],
                        "dob": row[3],
                        "gender": row[4],
                        "phone": row[5],
                        "email": row[6],
                        "insurance_company": row[7],
                        "member_id": row[8],
                        "group_id": row[9],
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
        schedule_id: str,
        patient_id: str
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
                "schedule_id": schedule_id,
                "patient_id": patient_id
            }

        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }

    def get_user(self, username : str, password : str) -> dict:
        query = """
            SELECT user_id, username, password, session_id
            FROM user
            WHERE username = ? AND password = ?
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (username, password))
                user = cursor.fetchone()

            if user:
                return {
                    "status": True,
                    "message": "User authenticated",
                    "data": {
                        "user_id": user[0],
                        "username": user[1],
                        "session_id": user[3]
                    }
                }

            else:
                query = """
                    SELECT user_id, username 
                    FROM user
                    WHERE username = ?
                """
                cursor.execute(query, (username,))
                user = cursor.fetchone()

                if user:
                    return {
                        "status": False,
                        "message": "Username exists but incorrect password"
                    }
                else:
                    return {
                        "status": False,
                        "message": "User doesn't exist create new account!!"
                    }

        except:
            return {
                "status": False,
                "message": "Error during authentication"
            }


    def create_user(self, username : str, password : str) -> dict:
        """Create a new user account."""
        session_id = str(uuid.uuid4())

        query = """
            INSERT INTO user (user_id, username, password, session_id)
            VALUES (?, ?, ?, ?)
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (str(uuid.uuid4()), username, password, session_id))
                conn.commit()

            return {
                "status": True,
                "message": "User created successfully",
                "data": {
                    "username": username,
                    "session_id": session_id
                }
            }

        except sqlite3.IntegrityError:
            return {
                "status": False,
                "message": "Username already exists"
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
def get_patient_details_tool(patient_id: str):
    """Get full patient details (name, email, phone, insurance) by patient_id.

    Call this after search_patient_tool or insert_patient_tool returns a patient_id.
    Use the returned data to compose confirmation emails and verify patient info.

    Args:
        patient_id: The patient_id returned by search_patient_tool or insert_patient_tool
    """
    db = Tools()
    return db.get_patient_details(patient_id)


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
    """Check if a specific doctor slot is available for a given specialty, day, and time.

    Use this ONLY when the user provides an exact day and time.
    If the user says something vague like 'Wednesday morning', use
    get_available_slots_tool instead.

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
def book_appointment_tool(schedule_id: str, patient_id: str):
    """Book a confirmed available appointment slot.

    Only call this after doctor_availability_tool returns a valid schedule_id
    AND the user has confirmed they want to proceed.
    Marks the slot as booked — this cannot be undone.

    Args:
        schedule_id: The schedule_id returned by doctor_availability_tool
        patient_id: The patient_id from search_patient_tool or insert_patient_tool
    """
    db = Tools()
    return db.book_appointment(schedule_id, patient_id)

@tool
def get_available_slots_tool(
    day_of_week: str,
    speciality: str
):
    """Get all available time slots for a given day and specialty.

    Call this when the user has NOT specified an exact time, or says
    something vague like 'Wednesday morning' or 'any time Thursday'.
    Returns a list of available slots with schedule_id, doctor name, and time.

    The response includes schedule_id for each slot. Store the schedule_id
    of the slot the user picks and pass it to book_appointment_tool.

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
    receiver: str,
    body: str,
    sender: str = "clinic@medical.com"
):
    """Create a dummy email for confirmation of doctor appointment.

    Args:
        subject: Subject line of the email
        receiver: Receiver's email address (patient's email)
        body: Body content of the email
        sender: Sender email (defaults to clinic@medical.com)
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


def build_confirmation_email(patient_data: dict, slot_data: dict, duration: int) -> dict:
    """Build a formatted confirmation email from patient and slot data.

    Args:
        patient_data: dict with keys: first_name, last_name, email
        slot_data: dict with keys: doctor_name, speciality, day_of_week, time_slot
        duration: appointment duration in minutes (15 or 30)

    Returns:
        dict with keys: subject, receiver, body
    """
    patient_name = f"{patient_data['first_name']} {patient_data['last_name']}"
    doctor_name = slot_data['doctor_name']
    speciality = slot_data['speciality']
    day = slot_data['day_of_week']
    time_slot = slot_data['time_slot']
    schedule_id = slot_data.get('schedule_id', 'N/A')

    subject = f"Appointment Confirmation - Dr. {doctor_name} ({speciality})"

    body = (
        f"Dear {patient_name},\n\n"
        f"Your appointment has been confirmed.\n\n"
        f"Doctor: Dr. {doctor_name}\n"
        f"Specialty: {speciality}\n"
        f"Day: {day}\n"
        f"Time: {time_slot}\n"
        f"Duration: {duration} minutes\n"
        f"Confirmation ID: {schedule_id}\n\n"
        f"If you need to reschedule or cancel, please contact us.\n\n"
        f"Best regards,\n"
        f"Medical Scheduling Team"
    )

    return {
        "subject": subject,
        "receiver": patient_data['email'],
        "body": body
    }




TOOLS = [
    search_patient_tool,
    get_patient_details_tool,
    insert_patient_tool,
    doctor_availability_tool,
    get_available_slots_tool,
    book_appointment_tool,
    send_email_tool,
]