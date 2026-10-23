from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector

app = FastAPI()


# Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pediatric_clinic"
    )


# Child data
class Child(BaseModel):
    name: str
    age: int
    guardian_name: str
    gender: str | None = None
    doctor_name: str | None = None
    appointment_date: str | None = None
    diagnosis: str | None = None


# Home page
@app.get("/")
def home():
    return {
        "message": "Welcome to Pediatric Clinic Management System"
    }


# Add a child to the database
@app.post("/children")
def add_child(child: Child):
    connection = get_db_connection()
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
        child.diagnosis
    )

    try:
        cursor.execute(query, values)
        connection.commit()
        return {
            "message": "Child added successfully",
            "id": cursor.lastrowid
        }
    finally:
        cursor.close()
        connection.close()


# Get all children from the database
@app.get("/children")
def get_children():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM children")
        children = cursor.fetchall()
        return {"children": children}
    finally:
        cursor.close()
        connection.close()