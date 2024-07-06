from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from app.models import Immunization, ImmunizationCreateModel, ImmunizationUpdateModel, User
from app.middlewares.authware import is_nurse_or_doctor, is_chew,get_current_user
from app.utils import encode_input

router = APIRouter(prefix="/api/immunizations", tags=["immunizations"])


@router.post(
    "/",
    response_model=Immunization,
    status_code=201,
    dependencies=[Depends(is_chew)],
)
async def create_immunization(
    immunization_data: ImmunizationCreateModel, 
    current_user: User = Depends(get_current_user)
):
    """Create a new immunization record."""
    existing_client = await Immunization.find_one({"card_no": immunization_data.card_no})
    if existing_client:
        raise HTTPException(status_code=400, detail="Card number already exists")
    new_immunization = Immunization(
        **immunization_data.dict(),
        entered_by=current_user.username,
        updated_at=datetime.utcnow()
    )
    _ = await new_immunization.insert()
    return new_immunization


@router.get("/", response_model=List[Immunization])
async def list_immunizations():
    """Retrieve a list of immunizations."""
    immunizations = await Immunization.find_all().to_list()
    if not immunizations:
        raise HTTPException(status_code=404, detail="Immunization not found")
    return immunizations


@router.get("/{immunization}", response_model=Immunization)
async def get_immunization(card_no: str):
    """Retrieve a specific immunization record by ID."""
    immunization = await Immunization.find_one({"card_no": card_no})
    if not immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")
    return immunization


@router.put(
    "/{immunization}",
    response_model=Immunization,
    dependencies=[Depends(is_chew)],
)
async def update_immunization(
    card_no: str, 
    immunization_data: ImmunizationUpdateModel, 
    current_user: User = Depends(get_current_user),
):
    """Update an existing immunization record."""
    existing_immunization = await Immunization.find_one({"card_no": card_no})
    if not existing_immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")
    update_data = immunization_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data["entered_by"] = current_user.username

    # Ensure card_no is not changed
    if "card_no" in update_data:
        del update_data["card_no"]
    immunization = encode_input(update_data)
    _ = await existing_immunization.update({"$set": immunization})
    return existing_immunization

@router.delete(
    "/{immunization}",
    status_code=204,
    dependencies=[Depends(is_nurse_or_doctor)],
)
async def delete_immunization(card_no: str):
    """Delete an immunization record."""
    immunization = await Immunization.find_one({"card_no": card_no})
    if not immunization:
        raise HTTPException(status_code=404, detail="Immunization not found")
    _ = await immunization.delete()
    return {"message": "immmunization deleted"}
