from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from pydantic import BaseModel

from app.database import get_database
from app.models import Immunization

router = APIRouter()


# Define Pydantic models for request and response
class ImmunizationIn(BaseModel):
    name: str
    age: int
    gender: str
    vaccine_given: str
    date_of_vaccination: datetime


class ImmunizationOut(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    vaccine_given: str
    date_of_vaccination: datetime


# Endpoint to add immunization record
@router.post("/immunization/", response_model=ImmunizationOut)
async def add_immunization_record(
    immunization: ImmunizationIn, db: AsyncIOMotorClient = Depends(get_database)
):
    immunization_doc = immunization.dict()
    collection = db["immunizations"]
    result = await collection.insert_one(immunization_doc)
    inserted_immunization = await collection.find_one({"_id": result.inserted_id})
    return ImmunizationOut(**inserted_immunization)


# Endpoint to get all immunization records
@router.get("/immunization/", response_model=List[ImmunizationOut])
async def get_immunization_records(db: AsyncIOMotorClient = Depends(get_database)):
    collection = db["immunizations"]
    immunization_records = await collection.find({}).to_list(1000)
    return [ImmunizationOut(**record) for record in immunization_records]


# Endpoint to get immunization record by ID
@router.get("/immunization/{immunization_id}", response_model=ImmunizationOut)
async def get_immunization_record(
    immunization_id: str, db: AsyncIOMotorClient = Depends(get_database)
):
    collection = db["immunizations"]
    immunization_record = await collection.find_one({"_id": immunization_id})
    if immunization_record:
        return ImmunizationOut(**immunization_record)
    raise HTTPException(status_code=404, detail="Immunization record not found")
