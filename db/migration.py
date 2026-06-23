from db.schema import Schema
import sqlite3
import time


class Migration:
    def __init__(self):
        self.schema = Schema()

    def create_table(self, retries=3):
        tables = [
            ("patient", self.schema.create_patient_table),
            ("doctor_schedule", self.schema.create_doctor_table)
        ]

        results = {}

        for table_name, table_function in tables:
            attempt = 0

            while attempt < retries:
                try:
                    table_function()

                    results[table_name] = {
                        "status": "success",
                        "message": f"{table_name} table created successfully"
                    }
                    break

                except sqlite3.Error as e:
                    attempt += 1

                    if attempt < retries:
                        results[table_name] = {
                            "status": "retrying",
                            "message": f"Error creating {table_name}: {str(e)}. Retrying ({attempt}/{retries})..."
                        }
                        time.sleep(1)

                    else:
                        results[table_name] = {
                            "status": "failed",
                            "message": f"Failed to create {table_name} after {retries} attempts",
                            "error": str(e)
                        }

                except Exception as e:
                    results[table_name] = {
                        "status": "failed",
                        "message": f"Unexpected error while creating {table_name}",
                        "error": str(e)
                    }
                    break

        return results
