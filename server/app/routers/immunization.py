from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from app.models import Immunization, User, Roles
from app.middlewares.authware import is_user_doctor, is_chew, is_nurse_or_doctor, get_current_user

router = APIRouter()

@router.post(
    "/immunizations",
    response_model=Immunization,
    status_code=201,
    dependencies=[Depends(is_chew)],
)
async def create_immunization(immunization: Immunization):
    """Create a new immunization record."""
    new_immunization = await Immunization.save(immunization)
    return new_immunization


@router.get("/immunizations", response_model=List[Immunization])
async def list_immunizations():
    """Retrieve a list of immunizations."""
    immunizations = await Immunization.find_all()
    if not immunizations:
        raise HTTPException(status_code=404, detail="Immunization not found")
    return immunizations


@router.get("/immunizations/{immunization_id}", response_model=Immunization)
async def get_immunization(immunization_id: str):
    """Retrieve a specific immunization record by ID."""
    immunization = await Immunization.find_one({"_id": immunization_id})
    if not immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")
    return immunization


@router.put(
    "/immunizations/{immunization_id}",
    response_model=Immunization,
    dependencies=[Depends(is_chew)],
)
async def update_immunization(immunization_id: str, immunization: Immunization):
    """Update an existing immunization record."""
    existing_immunization = await Immunization.find_one({"_id": immunization_id})
    if not existing_immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")
    immunization.updated_at = datetime.utcnow()
    updated_immunization = await Immunization.replace(existing_immunization, immunization)
    return updated_immunization


@router.delete(
    "/immunizations/{immunization_id}",
    status_code=204,
    dependencies=[Depends(is_nurse_or_doctor)],
)
async def delete_immunization(immunization_id: str):
    """Delete an immunization record."""
    immunization = await Immunization.get(immunization_id)
    if not immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")
    await immunization.delete()
