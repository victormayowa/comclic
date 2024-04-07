from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.models import Finance, User, Roles
from app.database import db

router = APIRouter()


async def get_current_user(username: str = Depends(User)):
    """Dependency to get the current user."""
    return await username


async def is_user_accountant(current_user: User = Depends(get_current_user)):
    """Dependency to check if the current user is an accountant."""
    if Roles.AC not in current_user.roles:
        raise HTTPException(
            status_code=403, detail="Forbidden: Only accountants are allowed"
        )


async def is_user_doctor(current_user: User = Depends(get_current_user)):
    """Dependency to check if the current user is a doctor."""
    if Roles.DR not in await current_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only doctors are allowed to review financial records",
        )


@router.post(
    "/financial-records",
    response_model=Finance,
    status_code=201,
    dependencies=[Depends(is_user_accountant)],
)
async def create_financial_record(finance: Finance):
    """Create a new financial record."""
    new_finance = await db.save(finance)
    return new_finance


@router.get("/financial-records", response_model=List[Finance])
async def list_financial_records():
    """Retrieve a list of financial records."""
    financial_records = await Finance.find_all()
    return financial_records


@router.get("/financial-records/{record_id}", response_model=Finance)
async def get_financial_record(record_id: str):
    """Retrieve a specific financial record by ID."""
    financial_record = await Finance.find_one({"_id": record_id})
    if not financial_record:
        raise HTTPException(status_code=404, detail="Financial record not found")
    return financial_record


@router.put(
    "/financial-records/{record_id}",
    response_model=Finance,
    dependencies=[Depends(is_user_accountant)],
)
async def update_financial_record(
    record_id: str, finance: Finance, current_user: User = Depends(get_current_user)
):
    """Update an existing financial record."""
    existing_finance = await Finance.find_one({"_id": record_id})
    if not existing_finance:
        raise HTTPException(status_code=404, detail="Financial record not found")

    if finance.reviewed_by_doctor and Roles.DR not in current_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only doctors can review financial records",
        )

    finance.updated_at = datetime.utcnow()
    updated_finance = await db.replace(existing_finance, finance)
    return updated_finance
