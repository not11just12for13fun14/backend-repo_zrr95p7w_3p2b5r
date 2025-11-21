"""
Database Schemas for Health Tracking App

Each Pydantic model below represents a MongoDB collection. The collection
name is the lowercase of the class name.

Examples:
- Doctor -> "doctor"
- Patient -> "patient"

These schemas are used for validation and also to power the database viewer.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import date, datetime

# ----------------------------- Core Entities -----------------------------

class Doctor(BaseModel):
    name: str = Field(..., description="Full name of the doctor")
    specialization: str = Field(..., description="Medical specialization")
    qualification: str = Field(..., description="Degrees and certifications")
    current_hospital: str = Field(..., description="Current hospital or clinic")
    years_of_experience: int = Field(..., ge=0, le=80, description="Years of experience")
    location: str = Field(..., description="City / Area")
    profile_photo: Optional[str] = Field(None, description="URL of profile photo")

class PatientMedicalInfo(BaseModel):
    blood_group: Optional[str] = Field(None, description="Blood group (e.g., O+, A-)" )
    allergies: Optional[List[str]] = Field(default_factory=list)
    current_medication: Optional[List[str]] = Field(default_factory=list)
    past_medication: Optional[List[str]] = Field(default_factory=list)
    chronic_disease: Optional[List[str]] = Field(default_factory=list)
    assigned_doctor: Optional[str] = Field(None, description="Doctor ID or name")

class Patient(BaseModel):
    patient_id: str = Field(..., description="Unique patient ID")
    full_name: str
    date_of_birth: date
    gender: Literal["Male", "Female", "Other"]
    contact_number: str
    alternate_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: str
    profile_photo: Optional[str] = None
    medical_information: PatientMedicalInfo

class Family(BaseModel):
    family_id: str
    contact_number: str
    address: str

class Admin(BaseModel):
    admin_id: str
    full_name: str
    email: EmailStr
    contact_number: str
    profile_photo: Optional[str] = None
    role: Literal["Super Admin", "Hospital Admin", "Receptionist", "Staff", "Other"]

# ----------------------------- Permissions & Roles -----------------------------

class AccessPermission(BaseModel):
    subject: Literal["Doctors", "Patients", "Appointments", "Payments"]
    permissions: List[str] = Field(..., description="List of actions allowed")

# ----------------------------- Operational Collections -----------------------------

class Appointment(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_time: datetime
    status: Literal["Scheduled", "Completed", "Cancelled", "Reassigned"] = "Scheduled"
    notes: Optional[str] = None

class Payment(BaseModel):
    appointment_id: Optional[str] = None
    patient_id: str
    amount: float
    currency: Literal["USD", "INR", "EUR", "GBP", "Other"] = "USD"
    status: Literal["Pending", "Approved", "Refunded", "Failed"] = "Pending"
    method: Optional[str] = None

class Article(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    body: str
    tags: List[str] = Field(default_factory=list)

class Emergency(BaseModel):
    area: str
    number: str
    description: Optional[str] = None

class Hospital(BaseModel):
    name: str
    address: str
    city: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    phone: Optional[str] = None

class HealthMetric(BaseModel):
    patient_id: str
    timestamp: datetime
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    blood_oxygen_level: Optional[float] = None
    wbc_count: Optional[float] = None
    platelet_count: Optional[float] = None
    sugar_level: Optional[float] = None
    vitamin_deficiencies: Optional[List[str]] = Field(default_factory=list)

class Report(BaseModel):
    patient_id: str
    title: str
    report_date: date
    file_url: Optional[str] = None
    notes: Optional[str] = None

# ----------------------------- AI Nurse -----------------------------

class Reminder(BaseModel):
    patient_id: str
    reminder_type: Literal[
        "Appointment",
        "Medication",
        "Diet",
        "Hydration",
        "Call"
    ]
    message: str
    due_at: datetime
    dosage: Optional[str] = None
    appointment_id: Optional[str] = None

