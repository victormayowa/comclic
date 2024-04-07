from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime
from typing import List

from app.models import Immunization, User, Roles
from app.database import db

router = APIRouter()


async def get_current_user(username: str = Depends(User)):
    """Dependency to get the current user."""
    return username


async def is_user_accountant(current_user: User = Depends(get_current_user)):
    """Dependency to check if the current user is an accountant."""
    if Roles.AC in current_user.roles:
        raise HTTPException(
            status_code=403, detail="Forbidden: Accountants are not allowed"
        )


@router.post(
    "/immunizations",
    response_model=Immunization,
    status_code=201,
    dependencies=[Depends(is_user_accountant)],
)
async def create_immunization(immunization: Immunization):
    """Create a new immunization record."""
    new_immunization = await db.save(immunization)
    return new_immunization


@router.get("/immunizations", response_model=List[Immunization])
async def list_immunizations():
    """Retrieve a list of immunizations."""
    immunizations = await Immunization.find_all()
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
    dependencies=[Depends(is_user_accountant)],
)
async def update_immunization(immunization_id: str, immunization: Immunization):
    """Update an existing immunization record."""
    existing_immunization = await Immunization.find_one({"_id": immunization_id})
    if not existing_immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")
    immunization.updated_at = datetime.utcnow()
    updated_immunization = await db.replace(existing_immunization, immunization)
    return updated_immunization
