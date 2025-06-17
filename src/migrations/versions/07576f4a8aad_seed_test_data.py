"""Seed test data

Revision ID: 07576f4a8aad
Revises: 5fada68de757
Create Date: 2025-06-17 13:50:38.026468

"""

from datetime import date
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "07576f4a8aad"
down_revision: Union[str, Sequence[str], None] = "5fada68de757"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add seed data."""
    # Add patients
    op.bulk_insert(
        sa.table(
            "patient",
            sa.Column("id", sa.Integer()),
            sa.Column("first_name", sa.String()),
            sa.Column("last_name", sa.String()),
            sa.Column("date_of_birth", sa.Date()),
            sa.Column("sex", sa.Enum("male", "female", name="patient_sex_enum")),
        ),
        [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": date(1990, 1, 15),
                "sex": "male",
            },
            {
                "id": 2,
                "first_name": "Jane",
                "last_name": "Smith",
                "date_of_birth": date(1985, 6, 22),
                "sex": "female",
            },
        ],
    )

    # Add clinicians
    op.bulk_insert(
        sa.table(
            "clinician",
            sa.Column("id", sa.Integer()),
            sa.Column("first_name", sa.String()),
            sa.Column("last_name", sa.String()),
            sa.Column("registration_id", sa.String()),
        ),
        [
            {
                "id": 1,
                "first_name": "Dr",
                "last_name": "House",
                "registration_id": "MD12345",
            },
            {
                "id": 2,
                "first_name": "Dr",
                "last_name": "Wilson",
                "registration_id": "MD67890",
            },
        ],
    )

    # Add medications
    op.bulk_insert(
        sa.table(
            "medication",
            sa.Column("id", sa.Integer()),
            sa.Column("code", sa.String()),
            sa.Column("code_name", sa.String()),
            sa.Column("code_system", sa.String()),
            sa.Column("strength_value", sa.Integer()),
            sa.Column("strength_unit", sa.String()),
            sa.Column(
                "form",
                sa.Enum(
                    "powder", "tablet", "capsule", "syrup", name="medication_form_enum"
                ),
            ),
        ),
        [
            {
                "id": 1,
                "code": "PARA500",
                "code_name": "Paracetamol",
                "code_system": "SNOMED-CT",
                "strength_value": 500,
                "strength_unit": "mg",
                "form": "tablet",
            },
            {
                "id": 2,
                "code": "IBUP400",
                "code_name": "Ibuprofen",
                "code_system": "SNOMED-CT",
                "strength_value": 400,
                "strength_unit": "mg",
                "form": "capsule",
            },
        ],
    )


def downgrade() -> None:
    """Remove seed data."""
    op.execute("DELETE FROM medication WHERE id IN (1, 2)")
    op.execute("DELETE FROM clinician WHERE id IN (1, 2)")
    op.execute("DELETE FROM patient WHERE id IN (1, 2)")
