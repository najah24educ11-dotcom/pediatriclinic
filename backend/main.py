import os

from fastapi import FastAPI
from pydantic import BaseModel

try:
    import mysql.connector
except ImportError:  # pragma: no cover - optional dependency
    mysql = None

app = FastAPI(title="Pediatric Clinic Management System")


def get_db_connection():
    if mysql is None:
        return None

    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "pediatric_clinic"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
        )
    except mysql.connector.Error:
        return None


class Child(BaseModel):
    name: str
    age: int
    guardian_name: str
    gender: str | None = None
    doctor_name: str | None = None
    appointment_date: str | None = None
    diagnosis: str | None = None


children_in_memory: list[Child] = []


@app.get("/")
def home():
    return {"message": "Welcome to Pediatric Clinic Management System"}


@app.post("/children")
def add_child(child: Child):
    connection = get_db_connection()
    if connection is None:
        children_in_memory.append(child)
        return {"message": "Child added successfully", "child": child.model_dump()}

    cursor = connection.cursor(dictionary=True)
    query = """
        INSERT INTO children
        (name, age, guardian_name, gender,
         doctor_name, appointment_date, diagnosis)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        child.name,
        child.age,
        child.guardian_name,
        child.gender,
        child.doctor_name,
        child.appointment_date,
        child.diagnosis,
    )

    try:
        cursor.execute(query, values)
        connection.commit()
        return {"message": "Child added successfully", "id": cursor.lastrowid}
    finally:
        cursor.close()
        connection.close()


@app.get("/children")
def get_children():
    connection = get_db_connection()
    if connection is None:
        return {"children": [child.model_dump() for child in children_in_memory]}

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM children")
        return {"children": cursor.fetchall()}
    finally:
        cursor.close()
        connection.close()