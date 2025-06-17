from datetime import date
from typing import Literal, Optional

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from patient_medication_app.database import Base

PatientSex = Literal["male", "female"]
MedicationForm = Literal["powder", "tablet", "capsule", "syrup"]
MedicationRequestStatus = Literal["active", "completed", "cancelled", "on-hold"]


class Patient(Base):
    """Patient model for the patient medication system."""

    __tablename__ = "patient"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[PatientSex] = mapped_column(
        Enum("male", "female", name="patient_sex_enum"), nullable=False
    )


class Clinician(Base):
    """Clinician model for the patient medication system."""

    __tablename__ = "clinician"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    registration_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )


class Medication(Base):
    """Medication model for the patient medication system."""

    __tablename__ = "medication"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    code_name: Mapped[str] = mapped_column(String(100), nullable=False)
    code_system: Mapped[str] = mapped_column(String(100), nullable=False)
    strength_value: Mapped[int] = mapped_column(Integer, nullable=False)
    strength_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    form: Mapped[MedicationForm] = mapped_column(
        Enum("powder", "tablet", "capsule", "syrup", name="medication_form_enum"),
        nullable=False,
    )


class MedicationRequest(Base):
    """Medication request model for the patient medication system."""

    __tablename__ = "medication_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_reference: Mapped[int] = mapped_column(
        Integer, ForeignKey("patient.id"), nullable=False
    )
    clinician_reference: Mapped[str] = mapped_column(
        String(20), ForeignKey("clinician.registration_id"), nullable=False
    )
    medication_reference: Mapped[str] = mapped_column(
        String(10), ForeignKey("medication.code"), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    prescribed_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True
    )  # Optional end date
    frequency: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[MedicationRequestStatus] = mapped_column(
        Enum(
            "active",
            "completed",
            "cancelled",
            "on-hold",
            name="medication_request_status_enum",
        ),
        nullable=False,
    )
