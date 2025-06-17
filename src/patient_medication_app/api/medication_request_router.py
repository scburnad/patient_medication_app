"""Medication Requests API Router
This module defines the API routes for managing medication request data in the Patient Medication service.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from patient_medication_app.core.models import (
    Clinician,
    Medication,
    MedicationRequest,
    Patient,
)
from patient_medication_app.database.connections import get_session
from patient_medication_app.schemas.medication_request import (
    MedicationRequestCreate,
    MedicationRequestResponse,
    MedicationRequestUpdate,
)

router = APIRouter(tags=["medication_requests"])


@router.get("/", response_model=list[MedicationRequestResponse])
async def get_medication_requests(
    status: Optional[str] = Query(None, description="Filter by request status"),
    prescribed_from: Optional[date] = Query(
        None, description="Filter by prescribed date from"
    ),
    prescribed_to: Optional[date] = Query(
        None, description="Filter by prescribed date to"
    ),
    db: Session = Depends(get_session),
):
    """
    Retrieve a list of medication requests with optional filters.

    Args:
        status: Optional filter by request status
        prescribed_from: Optional filter by prescribed date (from)
        prescribed_to: Optional filter by prescribed date (to)
        db: Database session dependency

    Returns:
        List of medication requests matching the filter criteria
    """
    query = (
        db.query(MedicationRequest)
        .join(Medication, MedicationRequest.medication_reference == Medication.code)
        .join(
            Clinician,
            MedicationRequest.clinician_reference == Clinician.registration_id,
        )
        .add_columns(
            Medication.code_name.label("medication_code_name"),
            Clinician.first_name.label("clinician_first_name"),
            Clinician.last_name.label("clinician_last_name"),
        )
    )

    if status:
        query = query.filter(MedicationRequest.status == status)

    if prescribed_from:
        query = query.filter(MedicationRequest.prescribed_date >= prescribed_from)

    if prescribed_to:
        query = query.filter(MedicationRequest.prescribed_date <= prescribed_to)

    results = query.all()
    response = []
    for req, medication_code_name, clinician_first_name, clinician_last_name in results:
        response.append(
            {
                **req.__dict__,
                "medication_code_name": medication_code_name,
                "clinician_first_name": clinician_first_name,
                "clinician_last_name": clinician_last_name,
            }
        )
    return response


@router.post("/", response_model=MedicationRequestResponse)
async def create_medication_request(
    request: MedicationRequestCreate, db: Session = Depends(get_session)
):
    """
    Create a new medication request.

    Args:
        request: The medication request data
        db: Database session dependency

    Returns:
        MedicationRequestResponse: The created medication request with related data

    Raises:
        HTTPException: If referenced patient, clinician or medication not found
    """

    # These validations might be overkill eg in a real application I'd expect the clinician
    # to have authorisation to prescribe medication, so they'd already be known to the system.

    # Validate patient exists
    patient = db.query(Patient).filter(Patient.id == request.patient_reference).first()
    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with id {request.patient_reference} not found",
        )

    # Validate clinician exists
    clinician = (
        db.query(Clinician)
        .filter(Clinician.registration_id == request.clinician_reference)
        .first()
    )
    if not clinician:
        raise HTTPException(
            status_code=404,
            detail=f"Clinician with registration ID {request.clinician_reference} not found",
        )

    # Validate medication exists
    medication = (
        db.query(Medication)
        .filter(Medication.code == request.medication_reference)
        .first()
    )
    if not medication:
        raise HTTPException(
            status_code=404,
            detail=f"Medication with code {request.medication_reference} not found",
        )

    # Create medication request
    db_request = MedicationRequest(**request.dict())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Return response with additional fields
    return {
        **db_request.__dict__,
        "medication_code_name": medication.code_name,
        "clinician_first_name": clinician.first_name,
        "clinician_last_name": clinician.last_name,
    }


@router.patch("/{medication_request_id}", response_model=MedicationRequestResponse)
async def update_medication_request(
    medication_request_id: int,
    request: MedicationRequestUpdate,
    db: Session = Depends(get_session),
):
    """
    Update an existing medication request.

    Only end_date, frequency, and status can be updated.

    Args:
        medication_request_id: The ID of the medication request to update
        request: The fields to update
        db: Database session dependency

    Returns:
        MedicationRequestResponse: The updated medication request

    Raises:
        HTTPException: If medication request not found
    """
    # Get existing request with related data
    db_request = (
        db.query(MedicationRequest)
        .join(Medication, MedicationRequest.medication_reference == Medication.code)
        .join(
            Clinician,
            MedicationRequest.clinician_reference == Clinician.registration_id,
        )
        .add_columns(
            Medication.code_name.label("medication_code_name"),
            Clinician.first_name.label("clinician_first_name"),
            Clinician.last_name.label("clinician_last_name"),
        )
        .filter(MedicationRequest.id == medication_request_id)
        .first()
    )

    if not db_request:
        raise HTTPException(
            status_code=404,
            detail=f"Medication request with id {medication_request_id} not found",
        )

    # Update only the provided fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_request[0], field, value)

    db.commit()
    db.refresh(db_request[0])

    # Return updated request with additional fields
    return {
        **db_request[0].__dict__,
        "medication_code_name": db_request.medication_code_name,
        "clinician_first_name": db_request.clinician_first_name,
        "clinician_last_name": db_request.clinician_last_name,
    }
