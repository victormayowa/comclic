from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from app.models import Patient, PatientCreateModel, PatientUpdateModel, User
from app.middlewares.authware import get_current_user, is_user_doctor
from app.utils import encode_input


router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(is_user_doctor)],
)
async def create_patient(patient: PatientCreateModel, current_user: User = Depends(get_current_user)):
    """Create a new patient record."""
    existing_patient = await Patient.find_one({"hospital_no": patient.hospital_no})
    if existing_patient:
        raise HTTPException(status_code=400, detail="Hospital number already exists")
    new_patient = Patient(
        **patient.dict(),
        entered_by=current_user.username,
        updated_at=datetime.utcnow()
    )
    _ = await new_patient.insert()
    return new_patient

@router.get(
    "/", 
    response_model=List[Patient], 
    dependencies=[Depends(is_user_doctor)]
)
async def list_patients():
    """Retrieve a list of patients."""
    patients = await Patient.find_all().to_list()
    return patients


@router.get(
    "/patient",
    response_model=Patient,
    dependencies=[Depends(is_user_doctor)],
)
async def get_patient(hospital_no: str):
    """Retrieve a specific patient's details by ID."""
    patient = await Patient.find_one({"hospital_no": hospital_no})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put(
    "/patient",
    response_model=Patient,
    dependencies=[Depends(is_user_doctor)],
)
async def update_patient(
    hospital_no: str,
    patient_data: PatientUpdateModel,
    current_user: User = Depends(get_current_user),
):
    """Update an existing patient record."""
    existing_patient = await Patient.find_one({"hospital_no": hospital_no})
    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    update_data = patient_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data["entered_by"] = current_user.username
    if 'hospital_no' in update_data:
        del update_data['hospital_no']
    patient = encode_input(update_data)

    _ = await existing_patient.update({"$set": patient})
    return existing_patient


@router.delete(
    "/{patient}", status_code=204, dependencies=[Depends(is_user_doctor)]
)
async def delete_patient(hospital_no: str):
    """Delete a patient record."""
    patient = await Patient.find_one({"hospital_no": hospital_no})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    _ = await patient.delete()
    return {"message": "Patient deleted"}
