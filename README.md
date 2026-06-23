# Medical Scheduler Agent

<img width="100%" alt="Medical Scheduler API" src="https://github.com/user-attachments/assets/4adef152-5080-4f63-973f-f1896b016900" />

A simple AI-powered medical scheduling backend built with **FastAPI**, **SQLite**, and **Faker** for synthetic data generation.

---

## Features

* Patient lookup
* Doctor availability checking
* Appointment booking
* Synthetic patient data generation
* Synthetic doctor schedule generation
* SQLite-based lightweight database

---

## Tech Stack

* Python
* FastAPI
* SQLite
* Faker
* uv

---

## Installation

Clone the project:

```bash
git clone <your-repo-url>
cd medical_agent
```

Install dependencies:

```bash
uv sync
```

Run server:

```bash
uvicorn main:app --reload
```

---

## API Endpoints

### 1. Health Check

**GET /**

Checks whether the server is running.

Response:

```json
{
  "message": "Server running"
}
```

---

### 2. Patient Lookup

**POST /patients/lookup**

Search for an existing patient.

Request:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "dob": "1999-05-12"
}
```

Response:

```json
{
  "status": true,
  "message": "Patient found",
  "data": {
    "patient_id": "uuid"
  }
}
```

---

### 3. Doctor Availability

**POST /doctors/availability**

Find doctor slots based on:

* day
* time
* duration
* specialty

Request:

```json
{
  "day_of_week": "Monday",
  "time_slot": "09:30",
  "duration": 15,
  "speciality": "Cardiology"
}
```

Fallback logic:

* Exact slot match
* Alternative slot on same day
* Alternative slot on another day
* No slots available

Response:

```json
{
  "status": true,
  "message": "Exact slot available",
  "data": []
}
```

---

### 4. Book Appointment

**POST /appointments/book**

Book an available doctor slot.

Request:

```json
{
  "schedule_id": "uuid"
}
```

Response:

```json
{
  "status": true,
  "message": "Appointment confirmed",
  "schedule_id": "uuid"
}
```

---

## Database Schema

### patient

Stores:

* Patient ID
* Name
* DOB
* Gender
* Phone
* Email
* Insurance details

### doctor_schedule

Stores:

* Schedule ID
* Doctor ID
* Doctor name
* Speciality
* Day of week
* Time slot
* Booking status

---

