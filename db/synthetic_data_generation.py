from faker import Faker
import sqlite3
import random
import uuid


class SyntheticDataGenerator:
    def __init__(self, db_path="database.db"):
        self.fake = Faker()
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.insurance_companies = [
            "Aetna",
            "Cigna",
            "UnitedHealth",
            "BlueCross"
        ]

    def generate_patient(self):
        gender = random.choice(["Male", "Female"])

        return {
            "patient_id": str(uuid.uuid4()),
            "first_name": (
                self.fake.first_name_male()
                if gender == "Male"
                else self.fake.first_name_female()
            ),
            "last_name": self.fake.last_name(),
            "dob": str(
                self.fake.date_of_birth(
                    minimum_age=18,
                    maximum_age=80
                )
            ),
            "gender": gender,
            "phone": self.fake.numerify(text="98########"),
            "email": self.fake.unique.email(),
            "insurance_company": random.choice(self.insurance_companies),
            "member_id": f"MEM-{random.randint(100000, 999999)}",
            "group_id": f"GRP-{random.randint(1000, 9999)}"
        }

    def generate_time_slots(self):
        slots = []

        for hour in range(9, 20):  # 09:00 to 19:00
            slots.append(f"{hour:02d}:00")

            if hour != 19:  # no 19:30
                slots.append(f"{hour:02d}:30")

        return slots

    def seed_doctors(self, doctor_count=5, slots_per_doctor=5):
        specialities = [
            "Cardiology",
            "Dermatology",
            "Orthopedics",
            "Neurology",
            "Pediatrics",
            "ENT"
        ]

        time_slots = self.generate_time_slots()
        doctors = []

        # Create unique doctors first
        for _ in range(doctor_count):
            gender = random.choice(["Male", "Female"])

            doctor = {
                "doc_id": str(uuid.uuid4()),
                "doctor_name": (
                    self.fake.name_male()
                    if gender == "Male"
                    else self.fake.name_female()
                ),
                "speciality": random.choice(specialities)
            }

            doctors.append(doctor)

        # Create multiple schedule slots for each doctor
        for doctor in doctors:
            selected_slots = random.sample(
                time_slots,
                min(slots_per_doctor, len(time_slots))
            )

            for slot in selected_slots:
                self.cursor.execute("""
                    INSERT INTO doctor_schedule (
                        schedule_id,
                        doc_id,
                        doctor_name,
                        speciality,
                        day_of_week,
                        time_slot,
                        is_booked
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    doctor["doc_id"],
                    doctor["doctor_name"],
                    doctor["speciality"],
                    random.randint(1, 7),
                    slot,
                    0
                ))

        self.conn.commit()
        return (
            f"{doctor_count} doctors with "
            f"{slots_per_doctor} slots each seeded successfully."
        )

    def seed_patients(self, count=50):
        for _ in range(count):
            patient = self.generate_patient()

            self.cursor.execute("""
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
            """, (
                patient["patient_id"],
                patient["first_name"],
                patient["last_name"],
                patient["dob"],
                patient["gender"],
                patient["phone"],
                patient["email"],
                patient["insurance_company"],
                patient["member_id"],
                patient["group_id"]
            ))

        self.conn.commit()
        return f"{count} patients seeded successfully."

    def close(self):
        self.conn.close()