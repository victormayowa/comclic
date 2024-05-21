from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from app.models import Patient
from app.middlewares.authware import is_user_doctor


router = APIRouter()


# async def get_current_user(username: str = Depends(User)):
#     """Dependency to get the current user."""
#     return username


# async def is_user_doctor(current_user: User = Depends(get_current_user)):
#     """Dependency to check if the current user is a doctor."""
#     if Roles.DR not in current_user.role:
#         raise HTTPException(status_code=403, detail="Forbidden: User is not a doctor")
#     return


@router.post(
    "/patients",
    response_model=Patient,
    status_code=201,
    dependencies=[Depends(is_user_doctor)],
)
async def create_patient(patient: Patient):
    """Create a new patient record."""
    new_patient = await Patient.save(patient)
    return new_patient

@router.get(
    "/patients", response_model=List[Patient], 
    dependencies=[Depends(is_user_doctor)]
)
async def list_patients():
    """Retrieve a list of patients."""
    patients = await Patient.find_all()
    return patients


@router.get(
    "/patients/{patient_id}",
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
    "/patients/{patient_id}",
    response_model=Patient,
    dependencies=[Depends(is_user_doctor)],
)
async def update_patient(patient_id: str, patient: Patient):
    """Update an existing patient record."""
    existing_patient = await Patient.find_one({"_id": patient_id})
    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.updated_at = datetime.utcnow()
    updated_patient = await Patient.replace(existing_patient, patient)
    return updated_patient


@router.delete(
    "/patients/{patient_id}", status_code=204, 
    dependencies=[Depends(is_user_doctor)]
)
async def delete_patient(patient_id: str):
    """Delete a patient record."""
    patient = await Patient.find_one({"_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await Patient.delete(patient)
