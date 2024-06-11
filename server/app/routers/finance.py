from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from app.models import Finance, User, Roles
from app.middlewares.auth import is_doctor_or_accountant, is_user_doctor
from app.middlewares.auth import authenticate

router = APIRouter(prefix="/api/finances", tags=["finances"])


@router.post(
    "/",
    status_code=201,
    dependencies=[Depends(is_doctor_or_accountant)],
)
async def create_financial_record(finance: Finance) -> Finance:
    """Create a new financial record."""
    new_finance = await Finance.save(finance)
    return new_finance


@router.get("/", dependencies=[Depends(authenticate)])
async def list_financial_records() -> List[Finance]:
    """Retrieve a list of financial records."""
    financial_records = await Finance.find_all().to_list()
    return financial_records


@router.get("/{record_id}", dependencies=[Depends(authenticate)])
async def get_financial_record(record_id: str) -> Finance:
    """Retrieve a specific financial record by ID."""
    financial_record = await Finance.find_one({"_id": record_id})
    if not financial_record:
        raise HTTPException(status_code=404, detail="Financial record not found")

    return financial_record


@router.put("/{record_id}")
async def update_financial_record(
    record_id: str,
    finance: Finance,
    current_user: User = Depends(is_doctor_or_accountant),
) -> Finance:
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
    updated_finance = await Finance.replace(existing_finance, finance)

    return updated_finance


@router.delete(
    "/{record_id}",
    status_code=204,
    dependencies=[Depends(is_user_doctor)],
)
async def delete_financial_record(record_id: str):
    """Delete a financial record."""
    financial_record = await Finance.get(record_id)
    if not financial_record:
        raise HTTPException(status_code=404, detail="Financial record not found")

    await financial_record.delete()
