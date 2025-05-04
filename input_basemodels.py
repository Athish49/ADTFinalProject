from pydantic import BaseModel
import datetime

class PatientBase(BaseModel):
    name: str
    age: int
    gender: int
    height: float
    weight: float

class Lifestyle(BaseModel):
    patient_id: int
    smoke: int
    alco: int
    active: int

class AppointmentCreate(BaseModel):
    patient_id: int
    appointment_type: str
    appointment_date: datetime.date

class TestDetails(BaseModel):
    appointment_id: int
    ap_hi: int
    ap_lo: int
    cholesterol: int
    gluc: int

class Prescription(BaseModel):
    appointment_id: int
    prescribed_date: datetime.date
    medicine_name: str
    dosage: str
    duration_days: int