import sqlite3

class Schema:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()

    def create_patient_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS patient(
            patient_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            insurance_company TEXT NOT NULL,
            member_id TEXT NOT NULL,
            group_id TEXT NOT NULL
        )
        '''

        self.cursor.execute(query)
        self.conn.commit()
        return "Patient Table Created"

    def create_doctor_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS doctor_schedule(
            schedule_id TEXT PRIMARY KEY,
            doc_id TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            speciality TEXT NOT NULL,
            day_of_week INTEGER NOT NULL CHECK(day_of_week BETWEEN 1 AND 7),
            time_slot TEXT NOT NULL,
            is_booked INTEGER NOT NULL DEFAULT 0
        )
        '''

        self.cursor.execute(query)
        self.conn.commit()
        return "Doctor Schedule Table Created"