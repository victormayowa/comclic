from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime 
from app.models import Finance, FinanceCreateModel, User, Roles
from app.middlewares.authware import is_accountant, get_current_user, is_user_doctor
from app.utils import encode_input

router = APIRouter(prefix="/api/finances", tags=["finances"])


@router.post(
    "/",
    response_model=Finance,
    dependencies=[Depends(is_accountant),],
)
async def create_finance(
    finance_data: FinanceCreateModel, current_user: User = Depends(get_current_user)
):
    """Create a new finance record."""
    existing_finance = await Finance.find_one({"record_id": finance_data.record_id})
    if existing_finance:
        raise HTTPException(status_code=400, detail="Record ID already exists")

    new_finance = Finance(
        **finance_data.dict(),
        entered_by=current_user.username,
        updated_at=datetime.utcnow()
    )
    await new_finance.insert()
    return new_finance

# get all finances information
@router.get(
    "/", 
    response_model=List[Finance],
    dependencies=[Depends(is_accountant)])
async def list_financial_records():
    """Retrieve a list of financial records."""
    financial_records = await Finance.find_all().to_list()
    return financial_records

# get one financial record using the specified financial id
@router.get(
    "/financial-record", 
    response_model=Finance, 
    dependencies=[Depends(is_accountant)]
)
async def get_financial_record(record_id: str):
    """Retrieve a specific financial record by ID."""
    financial_record = await Finance.find_one({"record_id": record_id})
    if not financial_record:
        raise HTTPException(status_code=404, detail="Financial record not found")
    return financial_record


@router.put(
    "/financial-record",
    response_model=Finance,
    dependencies=[Depends(is_user_doctor)],
)
async def update_financial_record(
    record_id: str, finance_data: Finance, current_user: User = Depends(get_current_user)
):
    """Update an existing financial record."""
    existing_finance = await Finance.find_one({"record_id": record_id})
    if not existing_finance:
        raise HTTPException(status_code=404, detail="Financial record not found")

    if finance_data.reviewed_by_doctor and Roles.DR not in current_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only doctors can review financial records",
        )

    update_data = finance_data.dict(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    update_data["entered_by"] = current_user.username

    if "record_id" in update_data:
        del update_data["record_id"]
    record = encode_input(update_data)

    _ = await existing_finance.update({"$set": record})
    return existing_finance

@router.delete(
    "/financial-record",
    status_code=204,
    dependencies=[Depends(is_user_doctor)],
)
async def delete_financial_record(record_id: str):
    """Delete a financial record."""
    financial_record = await Finance.find_one({"record_id": record_id})
    if not financial_record:
        raise HTTPException(status_code=404, detail="Financial record not found")
    _ = await financial_record.delete()
    print({"message": "Financial Record Deleted"})
