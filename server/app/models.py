"""
Pydantic Models for the API.
"""
from datetime import datetime, date
import re
from typing import List, Optional
from beanie import Indexed
import pymongo
from pydantic.types import Enum

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_serializer,
    field_validator,
    model_serializer,
    AliasChoices,
)
from pydantic_core import PydanticCustomError
from beanie import Document, before_event, Update


class InvalidatedToken(Document):
    token: str
    invalidated_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class Base(Document):
    """Base model"""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, v: datetime) -> str:
        """
        serializes datetime fields

        :param v: datetime object
        :type v: datetime

        :return: A string representation of the datetime object
        :rtype: str
        """

        return v.isoformat()

    @before_event(Update)
    def save_update_at(self) -> None:
        self.updated_at = datetime.utcnow()


class Clinic(Enum):
    Okeila_CHC = "Okeila CHC"
    Igbemo_CHC = "Igbemo CHC"
    Infant_Welfare_Clinic = "Infant Welfare Clinic"
    Staff_Clinic = "Staff Clinic"
class Patient(Base):
    hospital_no: str = Indexed(unique=True)
    name: str
    age: int
    gender: str
    reason_for_visit: Optional[str]
    complaint: str
    date_of_visit: date
    provisional_diagnosis: str
    differential_diagnosis: Optional[str]
    investigations: Optional[str]
    treatment: str
    referral: bool
    clinic: List[Clinic]
    entered_by: str

    class Config:
        json_schema_extra = {
            "example": {
                "hospital_no": "01/05/24",
                "name": "John Doe",
                "age": 30,
                "gender": "Male",
                "complaint": "Fever",
                "reason_for_visit": "hfollow uop",
                "date_of_visit": "2024-04-06",
                "provisional_diagnosis": "Malaria",
                "differential_diagnosis" : "Optional[str]",
                "treatment": "Prescribed medication",
                "investigations": "MP",
                "referral": False,
                "clinic": ["Okeila CHC"],
                "entered_by": "string",
            }
        }


class PatientUpdateModel(BaseModel):
    hospital_no: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    reason_for_visit: Optional[str] = None
    complaint: Optional[str] = None
    date_of_visit: Optional[date] = None
    provisional_diagnosis: Optional[str] = None
    differential_diagnosis: Optional[str] = None
    investigations: Optional[str] = None
    treatment: Optional[str] = None
    referral: Optional[bool] = None
    clinic: Optional[List[Clinic]] = None


class PatientCreateModel(BaseModel):
    hospital_no: str
    name: str
    age: int
    gender: str
    reason_for_visit: Optional[str]
    complaint: str
    date_of_visit: date
    provisional_diagnosis: str
    differential_diagnosis: Optional[str]
    investigations: Optional[str]
    treatment: str
    referral: bool
    clinic: List[Clinic]


class Vaccine(Enum):
    HBV = "HBV (Hepatitis B)"
    BCG = "BCG (Bacillus Calmette-Guérin)"
    OPV0 = "OPV0 (Oral Poliovirus Vaccine - Birth Dose)"
    PENTA1 = "Penta1/Rota/PCV1 (First dose of Pentavalent vaccine combined with Rotavirus and Pneumococcal Conjugate Vaccine)"
    PENTA2 = "Penta2/Rota/PCV2 (Second dose of Pentavalent vaccine combined with Rotavirus and Pneumococcal Conjugate Vaccine)"
    PENTA3 = "Penta3/Rota/PCV3 (Third dose of Pentavalent vaccine combined with Rotavirus and Pneumococcal Conjugate Vaccine)"
    IPV1 = "IPV1 (Inactivated Poliovirus Vaccine - First dose)"
    IPV2 = "IPV2 (Inactivated Poliovirus Vaccine - Second dose)"
    MEASLES1 = "Measles1 (First dose of Measles Vaccine)"
    MEASLES2 = "Measles2 (Second dose of Measles Vaccine)"
    YELLOW_FEVER = "Yellow Fever"
    MENA = "MenA (Meningococcal A Vaccine)"
    TETANUS1 = "Tetanus1 (First dose of Tetanus Vaccine)"
    TETANUS2 = "Tetanus2 (Second dose of Tetanus Vaccine)"
    TETANUS3 = "Tetanus3 (Third dose of Tetanus Vaccine)"
    TETANUS4 = "Tetanus4 (Fourth dose of Tetanus Vaccine)"
    TETANUS5 = "Tetanus5 (Fifth dose of Tetanus Vaccine)"


class Immunization(Base):
    card_no: str = Indexed(unique=True)
    DOB: str
    contact_no: str
    address: str
    caregivers_name: str
    name: str
    age: int
    gender: str
    vaccine_given: List[Vaccine]
    date_of_vaccination: date
    entered_by: str

    class Config:
        json_schema_extra = {
            "example": {
                "card_no": "12345",
                "DOB": "2024-04-06",
                "contact_no": "123-456-7890",
                "address": "123 Main St",
                "caregivers_name": "Jane Doe",
                "name": "John Doe",
                "age": 30,
                "gender": "Male",
                "vaccine_given": ["HBV", "BCG"],
                "date_of_vaccination": "2024-04-06",
                "entered_by": "Nurse Jane",
            }
        }


class ImmunizationCreateModel(BaseModel):
    card_no: str
    DOB: str
    contact_no: str
    address: str
    caregivers_name: str
    name: str
    age: int
    gender: str
    vaccine_given: List[Vaccine]
    date_of_vaccination: date


class ImmunizationUpdateModel(BaseModel):
    card_no: Optional[str] = None
    DOB: Optional[str] = None
    contact_no: Optional[str] = None
    address: Optional[str] = None
    caregivers_name: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    vaccine_given: Optional[List[Vaccine]] = None
    date_of_vaccination: Optional[date] = None

# Finance Model
class Source(Enum):
    DRF = "Drug Revolving Fund"
    SS = "Surgical Service"
    LS = "Laboratory/Radiological Service"
    NR = "New Registration/Booking Service"
    FR = "Folder retrieval"


class Finance(Base):
    record_id: str = Indexed(unique=True) # the record_id will be center_date_source_code
    record_officer: str
    payment_type: str
    source: List[Source]
    day_total_amount: float
    reviewed_by_doctor: bool
    entered_by: str

    class Config:
        json_schema_extra = {
            "example": {
                "record_officer": "Accountant Smith",
                "payment_type": "DRF",
                "day_total_amount": 10000.0,
                "source": ["DRF"],
                "reviewed_by_doctor": False,
                "entered_by": "User123",
            }
        }


class FinanceCreateModel(BaseModel):
    record_id: str  # this will be center_date_source_code
    record_officer: str
    payment_type: str
    source: List[Source]
    day_total_amount: float
    reviewed_by_doctor: bool


class FinanceUpdateModel(BaseModel):
    record_officer: Optional[str] = None
    payment_type: Optional[str] = None
    source: Optional[List[Source]] = None
    day_total_amount: Optional[float] = None
    reviewed_by_doctor: Optional[bool] = None


# User models for various

class Roles(Enum):
    DR = "Doctor"
    NR = "Nurse"
    AC = "Accountant"
    CH = "CHEW/RI/others"
class User(Base):
    """
    Represents a User of the PopChat app
    """

    username: str = Indexed(str, unique=True, index_type=pymongo.TEXT)
    email: EmailStr = Indexed(str, unique=True, index_type=pymongo.TEXT)
    password: str
    role: List[Roles]
    reset_token: str | None = None

    @model_serializer
    def serialize(self) -> dict:
        """
        serializes user object

        :return: A dict with the attributes.
        """

        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "id": str(self.id),
        }

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "username": "user123",
                "email": "user@example.com",
                "password": "securepassword",
                "roles": ["Doctor"],
            }
        }

    class Settings:
        name = "users"


class UserBase(BaseModel):
    """base user schema"""

    username: str | None = None
    email: EmailStr | None = None

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, v: str):
        """validates username"""

        USERNAME_REGEX = r"^[A-Za-z][A-Za-z0-9]{4,10}$"
        matches = re.fullmatch(USERNAME_REGEX, v)

        if matches is None:
            raise PydanticCustomError(
                "username_validation_error",
                "username must start with a letter and"
                " be between 4 and 10 characters long",
            )

        return v

    @field_validator("password", check_fields=False, mode="before")
    @classmethod
    def validate_password(cls, v: str):
        """validates password"""

        PASSWD_REGEX = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)"  # noqa: W605
            r"[A-Za-z\d\.+-=#_%|&@]{7,16}$"
        )  # noqa: W605
        if not re.fullmatch(PASSWD_REGEX, v):
            raise PydanticCustomError(
                "password_validation_error",
                "password must be between 7 and 16 characters long"
                " and contain at least one uppercase, one lowercase,"
                " one number and one of special character in .+-=#_%|&@",
            )

        return v

class UserRegister(UserBase):
    """user registration schema"""

    username: str
    email: EmailStr
    password: str
    role: List[Roles] = Field(..., description="User roles")
class UserLogin(UserBase):
    """user input schema"""

    password: str
class UserOut(UserBase):
    """user return schema"""

    id: str = Field(validation_alias=AliasChoices("_id", "id"))
class ResponseModel(BaseModel):
    """response model for the api"""

    message: str
    status_code: int
    data: dict | list | None = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    password: str
    password_confirm: str


class EmailSchema(BaseModel):
    email: List[EmailStr]
