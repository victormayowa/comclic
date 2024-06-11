from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.models import Immunization
from app.middlewares.auth import is_chew, is_nurse_or_doctor

router = APIRouter(prefix="/api/immunizations", tags=["immunizations"])


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(is_chew)],
)
async def create_immunization(immunization: Immunization) -> Immunization:
    """Create a new immunization record."""
    new_immunization = await Immunization.save(immunization)

    return new_immunization


@router.get("/")
async def list_immunizations() -> List[Immunization]:
    """Retrieve a list of immunizations."""
    immunizations = await Immunization.find_all().to_list()

    return immunizations


@router.get("/{immunization_id}")
async def get_immunization(immunization_id: str) -> Immunization:
    """Retrieve a specific immunization record by ID."""
    immunization = await Immunization.find_one({"_id": immunization_id})
    if not immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")

    return immunization


@router.put(
    "/{immunization_id}",
    response_model=Immunization,
    dependencies=[Depends(is_chew)],
)
async def update_immunization(immunization_id: str, immunization: Immunization):
    """Update an existing immunization record."""
    existing_immunization = await Immunization.find_one({"_id": immunization_id})
    if not existing_immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")

    updated_immunization = await Immunization.replace(
        existing_immunization, immunization
    )
    return updated_immunization


@router.delete(
    "/{immunization_id}",
    status_code=204,
    dependencies=[Depends(is_nurse_or_doctor)],
)
async def delete_immunization(immunization_id: str):
    """Delete an immunization record."""
    immunization = await Immunization.get(immunization_id)
    if not immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")

    await immunization.delete()
