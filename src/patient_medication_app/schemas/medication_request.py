from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

# Define valid status values
MedicationRequestStatus = Literal["active", "completed", "cancelled", "on-hold"]


class MedicationRequest(BaseModel):
    """Base schema for medication request data."""

    patient_reference: int = Field(..., description="Reference to the patient ID")
    clinician_reference: str = Field(
        ..., max_length=20, description="Reference to the clinician registration ID"
    )
    medication_reference: str = Field(
        ..., max_length=10, description="Reference to the medication code"
    )
    reason: str = Field(..., description="Reason for the medication request")
    prescribed_date: date = Field(..., description="Date the medication was prescribed")
    start_date: date = Field(..., description="Date to start taking the medication")
    end_date: Optional[date] = Field(
        None, description="Date to stop taking the medication"
    )
    frequency: str = Field(
        ..., max_length=50, description="How often to take the medication"
    )
    status: MedicationRequestStatus = Field(
        ..., description="Status of the medication request"
    )

    class Config:
        orm_mode = True
        json_encoders = {date: lambda v: v.isoformat()}


class MedicationRequestCreate(MedicationRequest):
    """Schema for creating a new medication request."""

    pass


class MedicationRequestUpdate(BaseModel):
    """Schema for updating an existing medication request."""

    end_date: Optional[date] = Field(
        None, description="Date to stop taking the medication"
    )
    frequency: Optional[str] = Field(
        None, max_length=50, description="How often to take the medication"
    )
    status: Optional[MedicationRequestStatus] = Field(
        None, description="Status of the medication request"
    )

    class Config:
        orm_mode = True
        extra = "forbid"  # Prevent additional fields


class MedicationRequestResponse(MedicationRequest):
    """Schema for returning medication request data."""

    id: int = Field(..., description="Unique identifier for the medication request")
    medication_code_name: str = Field(..., description="Name of the medication")
    clinician_first_name: str = Field(
        ..., description="First name of the prescribing clinician"
    )
    clinician_last_name: str = Field(
        ..., description="Last name of the prescribing clinician"
    )


class MedicationRequestListResponse(BaseModel):
    """Schema for returning a list of medication requests."""

    medication_requests: list[MedicationRequestResponse] = Field(
        ..., description="List of medication requests"
    )

    class Config:
        orm_mode = True
        json_encoders = {date: lambda v: v.isoformat()}
