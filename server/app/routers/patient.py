from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from app.models import Patient
from app.middlewares.auth import is_user_doctor


router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(is_user_doctor, use_cache=False)],
)
async def create_patient(patient: Patient) -> Patient:
    """Create a new patient record."""
    new_patient = await Patient.save(patient)

    return new_patient


@router.get("/", response_model=List[Patient], dependencies=[Depends(is_user_doctor)])
async def list_patients():
    """Retrieve a list of patients."""
    patients = await Patient.find_all().to_list()

    return patients


@router.get(
    "/{patient_id}",
    response_model=Patient,
    dependencies=[Depends(is_user_doctor)],
)
async def get_patient(patient_id: str):
    """Retrieve a specific patient's details by ID."""
    patient = await Patient.find_one({"_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@router.put(
    "/{patient_id}",
    dependencies=[Depends(is_user_doctor)],
)
async def update_patient(patient_id: str, patient: Patient) -> Patient:
    """Update an existing patient record."""
    existing_patient = await Patient.find_one({"_id": patient_id})
    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient.updated_at = datetime.utcnow()
    updated_patient = await Patient.replace(existing_patient, patient)

    return updated_patient


@router.delete("/{patient_id}", status_code=204, dependencies=[Depends(is_user_doctor)])
async def delete_patient(patient_id: str):
    """Delete a patient record."""
    patient = await Patient.find_one({"_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    await patient.delete()
