from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: str
    name: str
    created_at: datetime

@dataclass
class MedicalRecord:
    id: str
    patient_id: str
    record_type: str  # 'prescription' or 'lab_result'
    details: dict
    created_at: datetime