from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

from db.migration import Migration
from db.synthetic_data_generation import SyntheticDataGenerator
from tools import Tools

from agent.setup_model import download_model

app = FastAPI()

class PatientLookupRequest(BaseModel):
    first_name: str
    last_name: str
    dob: str


class DoctorAvailabilityRequest(BaseModel):
    day_of_week: Literal[
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ]
    time_slot: str
    duration: Literal[15, 30]
    speciality: Literal[
        "Cardiology",
        "Dermatology",
        "Orthopedics",
        "Neurology",
        "Pediatrics",
        "ENT"
    ]


class BookAppointmentRequest(BaseModel):
    schedule_id: str


@app.on_event("startup")
def startup():
    print("Running migrations...")

    migration = Migration()
    migration_result = migration.create_table()

    if migration_result:
        print(migration_result)
    else:
        print("Migration failed!")
        return

    print("Seeding synthetic data...")

    generator = SyntheticDataGenerator()

    seed_result = generator.seed_patients(50)
    seed_doctor_result = generator.seed_doctors(7, 7)

    print(seed_result)
    print(seed_doctor_result)

    generator.close()

    print("Checking model...")

    model_status = download_model()

    if model_status:
        print("Model ready.")
    else:
        print("Model unavailable. Continuing startup without model.")

    print("Startup completed successfully.")


@app.get("/")
def start():
    return {"message": "Server running"}


@app.post("/patients/lookup")
def patient_lookup(payload: PatientLookupRequest):
    tools = Tools()

    return tools.search_patient(
        payload.first_name,
        payload.last_name,
        payload.dob
    )


@app.post("/doctors/availability")
def available_doctor(payload: DoctorAvailabilityRequest):
    tools = Tools()

    return tools.doctor_availibility(
        payload.day_of_week,
        payload.time_slot,
        payload.duration,
        payload.speciality
    )

@app.post("/appointments/book")
def book_appointment(payload: BookAppointmentRequest):
    tools = Tools()

    return tools.book_appointment(
        payload.schedule_id
    )