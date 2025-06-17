from datetime import date

import pytest
from sqlalchemy.orm import Session

from patient_medication_app.core.models import (
    Clinician,
    Medication,
    MedicationRequest,
    Patient,
)


@pytest.fixture
def sample_patient(db_session: Session):
    patient = Patient(
        first_name="John", last_name="Doe", date_of_birth=date(1990, 1, 1), sex="male"
    )
    db_session.add(patient)
    db_session.commit()
    return patient


@pytest.fixture
def sample_clinician(db_session: Session):
    clinician = Clinician(first_name="Dr", last_name="House", registration_id="MD12345")
    db_session.add(clinician)
    db_session.commit()
    return clinician


@pytest.fixture
def sample_medication(db_session: Session):
    medication = Medication(
        code="PARA500",
        code_name="Paracetamol",
        code_system="SNOMED-CT",
        strength_value=500,
        strength_unit="mg",
        form="tablet",
    )
    db_session.add(medication)
    db_session.commit()
    return medication


@pytest.fixture
def sample_medication_requests(
    db_session: Session, sample_patient, sample_clinician, sample_medication
):
    request1 = MedicationRequest(
        patient_reference=sample_patient.id,
        clinician_reference=sample_clinician.registration_id,
        medication_reference=sample_medication.code,
        reason="Test reason",
        prescribed_date=date(2025, 6, 16),
        start_date=date(2025, 6, 16),
        frequency="twice daily",
        status="active",
    )
    request2 = MedicationRequest(
        patient_reference=sample_patient.id,
        clinician_reference=sample_clinician.registration_id,
        medication_reference=sample_medication.code,
        reason="Test reason 2",
        prescribed_date=date(2025, 6, 9),
        start_date=date(2025, 6, 9),
        frequency="twice daily",
        status="completed",
    )
    request3 = MedicationRequest(
        patient_reference=sample_patient.id,
        clinician_reference=sample_clinician.registration_id,
        medication_reference=sample_medication.code,
        reason="Test reason 3",
        prescribed_date=date(2025, 6, 2),
        start_date=date(2025, 6, 2),
        frequency="twice daily",
        status="on-hold",
    )
    request4 = MedicationRequest(
        patient_reference=sample_patient.id,
        clinician_reference=sample_clinician.registration_id,
        medication_reference=sample_medication.code,
        reason="Test reason 4",
        prescribed_date=date(2025, 5, 16),
        start_date=date(2025, 5, 16),
        frequency="twice daily",
        status="cancelled",
    )
    db_session.add_all([request1, request2, request3, request4])
    db_session.commit()
    for request in [request1, request2, request3, request4]:
        db_session.refresh(request)
    return [request1, request2, request3, request4]


class TestCreateMedicationRequest:
    def test_create_medication_request_success(
        self,
        client,
        db_session: Session,
        sample_patient,
        sample_clinician,
        sample_medication,
    ):

        # Store values before the session is closed
        patient_id = sample_patient.id
        clinician_first_name = sample_clinician.first_name
        medication_code_name = sample_medication.code_name

        request_data = {
            "patient_reference": sample_patient.id,
            "clinician_reference": sample_clinician.registration_id,
            "medication_reference": sample_medication.code,
            "reason": "Test reason",
            "prescribed_date": "2025-06-16",
            "start_date": "2025-06-16",
            "frequency": "twice daily",
            "status": "active",
        }

        response = client.post("/medication-requests/", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["patient_reference"] == patient_id
        assert data["medication_code_name"] == medication_code_name
        assert data["clinician_first_name"] == clinician_first_name

    def test_create_medication_request_invalid_patient(
        self, client, db_session: Session, sample_clinician, sample_medication
    ):
        request_data = {
            "patient_reference": 999,  # Non-existent patient
            "clinician_reference": sample_clinician.registration_id,
            "medication_reference": sample_medication.code,
            "reason": "Test reason",
            "prescribed_date": "2025-06-16",
            "start_date": "2025-06-16",
            "frequency": "twice daily",
            "status": "active",
        }

        response = client.post("/medication-requests/", json=request_data)
        assert response.status_code == 404
        assert "Patient with id 999 not found" in response.json()["detail"]

    def test_create_medication_request_invalid_clinician(
        self, client, db_session: Session, sample_patient, sample_medication
    ):
        request_data = {
            "patient_reference": sample_patient.id,
            "clinician_reference": "MD00001",  # Non-existent clinician
            "medication_reference": sample_medication.code,
            "reason": "Test reason",
            "prescribed_date": "2025-06-16",
            "start_date": "2025-06-16",
            "frequency": "twice daily",
            "status": "active",
        }

        response = client.post("/medication-requests/", json=request_data)
        assert response.status_code == 404
        assert (
            "Clinician with registration ID MD00001 not found"
            in response.json()["detail"]
        )

    def test_create_medication_request_invalid_medication(
        self, client, db_session: Session, sample_patient, sample_clinician
    ):
        request_data = {
            "patient_reference": sample_patient.id,
            "clinician_reference": sample_clinician.registration_id,
            "medication_reference": "MED00001",  # Non-existent medication
            "reason": "Test reason",
            "prescribed_date": "2025-06-16",
            "start_date": "2025-06-16",
            "frequency": "twice daily",
            "status": "active",
        }

        response = client.post("/medication-requests/", json=request_data)
        assert response.status_code == 404
        assert "Medication with code MED00001 not found" in response.json()["detail"]


class TestGetMedicationRequests:
    def test_get_medication_requests_no_filters(
        self, client, sample_medication_requests
    ):
        response = client.get("/medication-requests/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        ids = [req.id for req in sample_medication_requests]
        assert any(r["id"] in ids for r in data)

    def test_get_medication_requests_filter_by_status(
        self, client, sample_medication_requests
    ):
        response = client.get("/medication-requests/?status=active")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(r["status"] == "active" for r in data)

    def test_get_medication_requests_filter_by_date_range_all(
        self, client, sample_medication_requests
    ):
        response = client.get(
            "/medication-requests/?prescribed_from=2025-05-01&prescribed_to=2025-06-30"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert all(
            date.fromisoformat(r["prescribed_date"]) >= date(2025, 5, 1) for r in data
        )

    def test_get_medication_requests_filter_by_date_range_one(
        self, client, sample_medication_requests
    ):
        response = client.get(
            "/medication-requests/?prescribed_from=2025-06-15&prescribed_to=2025-06-30"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert all(
            date.fromisoformat(r["prescribed_date"]) >= date(2025, 5, 15) for r in data
        )

    def test_get_medication_requests_filter_by_date_range_and_status(
        self, client, sample_medication_requests
    ):
        response = client.get(
            "/medication-requests/?prescribed_from=2025-05-01&prescribed_to=2025-06-30&status=active"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert all(
            date.fromisoformat(r["prescribed_date"]) == date(2025, 6, 16) for r in data
        )

    def test_medication_request_list_response_structure(
        self, client, sample_medication_requests
    ):
        response = client.get("/medication-requests/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "id" in data[0]
        assert "medication_code_name" in data[0]
        assert "clinician_first_name" in data[0]
        assert "clinician_last_name" in data[0]

    def test_get_medication_request_not_found(self, client):
        response = client.get("/medication-requests/99999")
        assert response.status_code == 405


class TestUpdateMedicationRequest:
    def test_update_medication_request_success(
        self, client, sample_medication_requests
    ):
        update_data = {"status": "completed", "end_date": "2025-06-30"}

        response = client.patch(
            f"/medication-requests/{sample_medication_requests[0].id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["end_date"] == "2025-06-30"

    def test_update_medication_request_partial_data(
        self, client, sample_medication_requests
    ):
        # Only update frequency
        update_data = {"frequency": "three times daily"}
        response = client.patch(
            f"/medication-requests/{sample_medication_requests[0].id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "three times daily"
        # Other fields remain unchanged
        assert data["status"] == sample_medication_requests[0].status

    def test_update_medication_request_invalid_field(
        self, client, sample_medication_requests
    ):
        update_data = {"patient_reference": 999}  # Should not be allowed to update

        response = client.patch(
            f"/medication-requests/{sample_medication_requests[0].id}", json=update_data
        )
        assert response.status_code == 422  # Validation error

    def test_update_medication_request_not_found(self, client):
        response = client.patch(
            "/medication-requests/99999", json={"status": "completed"}
        )
        assert response.status_code == 404

    def test_update_medication_request_invalid_status(
        self, client, sample_medication_requests
    ):
        response = client.patch(
            f"/medication-requests/{sample_medication_requests[0].id}",
            json={"status": "not-a-valid-status"},
        )
        assert response.status_code == 422
