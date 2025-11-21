import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from database import db, create_document, get_documents
from schemas import (
    Doctor, Patient, Family, Admin, Appointment, Payment, Article, Emergency,
    Hospital, HealthMetric, Report, Reminder, AccessPermission
)

app = FastAPI(title="Health Tracking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Health Tracking Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# -------------------------- Helper Models --------------------------
class NearbyRequest(BaseModel):
    lat: float
    lng: float
    radius_km: float = 10

# -------------------------- CRUD Endpoints --------------------------
# Generic creators using database helpers; validation enforced by schemas

@app.post("/doctors")
def create_doctor(doctor: Doctor):
    doc_id = create_document("doctor", doctor)
    return {"id": doc_id, "message": "Doctor created"}

@app.get("/doctors")
def list_doctors():
    items = get_documents("doctor")
    return items

@app.post("/patients")
def create_patient(patient: Patient):
    doc_id = create_document("patient", patient)
    return {"id": doc_id, "message": "Patient created"}

@app.get("/patients")
def list_patients():
    items = get_documents("patient")
    return items

@app.post("/families")
def create_family(family: Family):
    doc_id = create_document("family", family)
    return {"id": doc_id, "message": "Family created"}

@app.get("/families")
def list_families():
    return get_documents("family")

@app.post("/admins")
def create_admin(admin: Admin):
    doc_id = create_document("admin", admin)
    return {"id": doc_id, "message": "Admin created"}

@app.get("/admins")
def list_admins():
    return get_documents("admin")

@app.post("/appointments")
def create_appointment(appt: Appointment):
    doc_id = create_document("appointment", appt)
    return {"id": doc_id, "message": "Appointment created"}

@app.get("/appointments")
def list_appointments():
    return get_documents("appointment")

@app.post("/payments")
def create_payment(payment: Payment):
    doc_id = create_document("payment", payment)
    return {"id": doc_id, "message": "Payment created"}

@app.get("/payments")
def list_payments():
    return get_documents("payment")

@app.post("/articles")
def create_article(article: Article):
    doc_id = create_document("article", article)
    return {"id": doc_id, "message": "Article created"}

@app.get("/articles")
def list_articles():
    return get_documents("article")

@app.post("/emergencies")
def create_emergency(emer: Emergency):
    doc_id = create_document("emergency", emer)
    return {"id": doc_id, "message": "Emergency contact created"}

@app.get("/emergencies")
def list_emergencies():
    return get_documents("emergency")

@app.post("/hospitals")
def create_hospital(h: Hospital):
    doc_id = create_document("hospital", h)
    return {"id": doc_id, "message": "Hospital created"}

@app.get("/hospitals")
def list_hospitals():
    return get_documents("hospital")

@app.post("/health-metrics")
def create_health_metric(metric: HealthMetric):
    doc_id = create_document("healthmetric", metric)
    return {"id": doc_id, "message": "Health metric recorded"}

@app.get("/health-metrics")
def list_health_metrics(patient_id: Optional[str] = None):
    filter_dict = {"patient_id": patient_id} if patient_id else {}
    return get_documents("healthmetric", filter_dict)

@app.post("/reports")
def create_report(report: Report):
    doc_id = create_document("report", report)
    return {"id": doc_id, "message": "Report uploaded"}

@app.get("/reports")
def list_reports(patient_id: Optional[str] = None):
    filter_dict = {"patient_id": patient_id} if patient_id else {}
    return get_documents("report", filter_dict)

@app.post("/reminders")
def create_reminder(rem: Reminder):
    doc_id = create_document("reminder", rem)
    return {"id": doc_id, "message": "Reminder created"}

@app.get("/reminders")
def list_reminders(patient_id: Optional[str] = None):
    filter_dict = {"patient_id": patient_id} if patient_id else {}
    return get_documents("reminder", filter_dict)

# -------------------------- Utility Features --------------------------

@app.post("/nearby-hospitals")
def nearby_hospitals(req: NearbyRequest):
    # naive radius filter on stored lat/lng if available
    from math import radians, sin, cos, sqrt, atan2

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    hospitals = get_documents("hospital")
    results: List[dict] = []
    for h in hospitals:
        lat, lng = h.get("location_lat"), h.get("location_lng")
        if lat is None or lng is None:
            continue
        dist = haversine(req.lat, req.lng, lat, lng)
        if dist <= req.radius_km:
            h_copy = dict(h)
            h_copy["distance_km"] = round(dist, 2)
            results.append(h_copy)

    results.sort(key=lambda x: x["distance_km"])  # closest first
    return results

# -------------------------- Simple AI Nurse Logic --------------------------

@app.post("/ai-nurse/medication-reminders")
def generate_medication_reminders(patient_id: str, times_per_day: int = 2, days: int = 7):
    now = datetime.utcnow()
    reminders = []
    for day in range(days):
        for t in range(times_per_day):
            due = now + timedelta(days=day, hours=9 + t*8)  # e.g., 9am and 5pm daily
            rem = Reminder(
                patient_id=patient_id,
                reminder_type="Medication",
                message="Time to take your medication",
                due_at=due
            )
            create_document("reminder", rem)
            reminders.append(rem)
    return {"created": len(reminders)}

@app.post("/ai-nurse/appointment-reminder")
def schedule_appointment_reminder(appointment_id: str, appointment_time: datetime, patient_id: str):
    due = appointment_time - timedelta(days=1)
    rem = Reminder(
        patient_id=patient_id,
        reminder_type="Appointment",
        message="Appointment tomorrow",
        due_at=due,
        appointment_id=appointment_id
    )
    rem_id = create_document("reminder", rem)
    return {"id": rem_id, "message": "Reminder scheduled"}

@app.post("/ai-nurse/hydration")
def hydration_reminders(patient_id: str, interval_hours: int = 2, hours: int = 12):
    now = datetime.utcnow()
    reminders = []
    for h in range(0, hours, interval_hours):
        due = now + timedelta(hours=h)
        rem = Reminder(
            patient_id=patient_id,
            reminder_type="Hydration",
            message="Drink water",
            due_at=due,
        )
        create_document("reminder", rem)
        reminders.append(rem)
    return {"created": len(reminders)}

@app.get("/dashboard/summary")
def dashboard_summary(patient_id: str):
    # aggregate a simple summary for the dashboard
    metrics = get_documents("healthmetric", {"patient_id": patient_id})
    reports = get_documents("report", {"patient_id": patient_id})

    latest = metrics[-1] if metrics else {}

    return {
        "disease": latest.get("chronic_disease", []),
        "medications": latest.get("current_medication", []),
        "reports_count": len(reports),
        "calendar": [],
        "health": {
            "bp": [latest.get("blood_pressure_systolic"), latest.get("blood_pressure_diastolic")],
            "oxygen": latest.get("blood_oxygen_level"),
            "wbc": latest.get("wbc_count"),
            "platelet": latest.get("platelet_count"),
            "sugar": latest.get("sugar_level"),
        },
        "vitamin_deficiencies": latest.get("vitamin_deficiencies", []),
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
