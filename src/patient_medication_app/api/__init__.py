"""API module for the Patient Medication service.
This module initializes API routes for managing patient medication data.
"""

from fastapi import APIRouter

from .medication_request_router import router as medication_request_router

api_router = APIRouter()


# Include the routers for patient, medication, and medication request
api_router.include_router(
    medication_request_router,
    prefix="/medication-requests",
    tags=["medication_requests"],
)

__all__ = ["api_router"]
