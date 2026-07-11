from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import uuid

from db.migration import Migration
from db.synthetic_data_generation import SyntheticDataGenerator
from tools import Tools

from agent.setup_model import download_model
from agent.agent import agent

from agent.loopagent import conversation

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
    patient_id: str


class CallAgent(BaseModel):
    user_input: str

class SessionResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str

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

    return tools.doctor_availability(
        payload.day_of_week,
        payload.time_slot,
        payload.duration,
        payload.speciality
    )

@app.post("/appointments/book")
def book_appointment(payload: BookAppointmentRequest):
    tools = Tools()

    return tools.book_appointment(
        payload.schedule_id, payload.patient_id
    )

@app.post("/agent")
def talk_to_agent(payload: CallAgent):
    return agent(payload.user_input)

@app.post("/session/start", response_model=SessionResponse)
def start_session():
    return SessionResponse(session_id=str(uuid.uuid4()))

@app.post("/chat/{session_id}", response_model=ChatResponse)
async def chat(session_id: str, body: ChatRequest):
    if not session_id.strip():
        return "Session ID cannot be empty"
    if not body.message.strip():
        return "Message cannot be empty"

    reply = conversation(body.message, session_id)
    return ChatResponse(session_id=session_id, reply=reply)
