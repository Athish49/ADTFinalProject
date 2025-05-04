from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import mysql.connector
from mysql.connector import Error
import random
import datetime
from input_basemodels import PatientBase, Lifestyle, AppointmentCreate, TestDetails, Prescription



app = FastAPI()

# ---------- DB CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='1234',
        database='healthcare_db'
    )



# ---------- ENDPOINTS ----------
@app.post("/patients/new")
def create_patient(patient: PatientBase):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        while True:
            patient_id = random.randint(10000000, 99999999)
            cursor.execute("SELECT COUNT(*) FROM patient_details WHERE patient_id = %s", (patient_id,))
            if cursor.fetchone()[0] == 0:
                break

        query = ("INSERT INTO patient_details (patient_id, name, age, gender, height, weight) "
                 "VALUES (%s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (patient_id, patient.name, patient.age, patient.gender, patient.height, patient.weight))
        conn.commit()
        return {"patient_id": patient_id}

    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.post("/patients/lifestyle")
def create_lifestyle(lifestyle: Lifestyle):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = ("INSERT INTO patient_lifestyle (patient_id, smoke, alco, active) "
                 "VALUES (%s, %s, %s, %s)")
        cursor.execute(query, (lifestyle.patient_id, lifestyle.smoke, lifestyle.alco, lifestyle.active))
        conn.commit()
        return {"message": "Lifestyle data added successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.get("/doctors")
def get_doctors():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM doctors")
        return cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.post("/appointments")
def create_appointment(appt: AppointmentCreate):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT doctor_id FROM doctors")
        doctor_ids = [row[0] for row in cursor.fetchall()]

        while True:
            appointment_id = random.randint(10000000, 99999999)
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE appointment_id = %s", (appointment_id,))
            if cursor.fetchone()[0] == 0:
                break

        assigned_doctor = random.choice(doctor_ids)
        query = ("INSERT INTO appointments (appointment_id, patient_id, doctor_id, appointment_date, appointment_type) "
         "VALUES (%s, %s, %s, %s, %s)")
        cursor.execute(query, (appointment_id, appt.patient_id, assigned_doctor, appt.appointment_date, appt.appointment_type))
        conn.commit()
        return {"appointment_id": appointment_id, "assigned_doctor_id": assigned_doctor}
    except Error as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.post("/tests")
def add_test_details(test: TestDetails):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        while True:
            test_id = random.randint(10000000, 99999999)
            cursor.execute("SELECT COUNT(*) FROM test_details WHERE test_id = %s", (test_id,))
            if cursor.fetchone()[0] == 0:
                break

        query = ("INSERT INTO test_details (test_id, appointment_id, ap_hi, ap_lo, cholesterol, gluc) "
                 "VALUES (%s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (test_id, test.appointment_id, test.ap_hi, test.ap_lo, test.cholesterol, test.gluc))
        conn.commit()
        return {"test_id": test_id}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.post("/prescriptions")
def prescribe_medicine(presc: Prescription):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        while True:
            prescription_id = random.randint(10000000, 99999999)
            cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE prescription_id = %s", (prescription_id,))
            if cursor.fetchone()[0] == 0:
                break

        # Business logic: assume patient with ap_hi > 140 or cholesterol > 2 is at risk
        cursor.execute("SELECT ap_hi, cholesterol FROM test_details WHERE appointment_id = %s", (presc.appointment_id,))
        test = cursor.fetchone()
        if not test:
            raise HTTPException(status_code=404, detail="Test data not found")

        ap_hi, chol = test
        if ap_hi > 140 or chol > 2:
            medicine_name = presc.medicine_name
        else:
            medicine_name = "Multivitamins"

        query = ("INSERT INTO prescriptions (prescription_id, appointment_id, prescribed_date, medicine_name, dosage, duration_days) "
                 "VALUES (%s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (prescription_id, presc.appointment_id, presc.prescribed_date, medicine_name, presc.dosage, presc.duration_days))
        conn.commit()
        return {"prescription_id": prescription_id}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.get("/patients/{patient_id}")
def get_patient_info(patient_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM patient_details WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        cursor.execute("SELECT * FROM patient_lifestyle WHERE patient_id = %s", (patient_id,))
        lifestyle = cursor.fetchone()

        return {"patient": patient, "lifestyle": lifestyle}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.get("/appointments/{patient_id}")
def get_appointments(patient_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM appointments WHERE patient_id = %s", (patient_id,))
        return cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.get("/records/{appointment_id}")
def get_records(appointment_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM test_details WHERE appointment_id = %s", (appointment_id,))
        test = cursor.fetchone()
        cursor.execute("SELECT * FROM prescriptions WHERE appointment_id = %s", (appointment_id,))
        presc = cursor.fetchone()

        return {"test_details": test, "prescription": presc}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.get("/fetch/{table}")
def fetch_table(table: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table}")
        return cursor.fetchall()
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@app.get("/get_analysis")
def get_analysis():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                pd.patient_id,
                pd.age,
                td.ap_hi,
                td.ap_lo,
                td.cholesterol,
                td.gluc
            FROM
                patient_details pd
            JOIN
                appointments a ON pd.patient_id = a.patient_id
            JOIN
                test_details td ON a.appointment_id = td.appointment_id
        """

        cursor.execute(query)
        results = cursor.fetchall()
        return results

    except Error as e:
        print("Error occurred:", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
        
        