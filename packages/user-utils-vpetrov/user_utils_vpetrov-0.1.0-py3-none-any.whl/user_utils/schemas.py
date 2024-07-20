"""
Schemas for the auth app
"""
import re
from enum import Enum
from typing import Optional
from datetime import date
from dateutil.relativedelta import relativedelta
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, Field, EmailStr, ConfigDict,\
    HttpUrl, field_serializer, field_validator


from .validators import validate_chilean_phone_number, validate_rut


PASS_REGEX_PATTERN = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
    r"(?=.*[@$!%*#?&+\-_.;,])[A-Za-z\d@$!#%*?&+\-_.;,]{6,20}$"
)


class GenderEnum(str, Enum):
    """
    Enum for the gender attribute.
    """
    M = "M"
    F = "F"


class UserBase(BaseModel):
    """
    Base schema for the User model.
    """
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=15, max_length=15)
    rut: str = Field(..., min_length=11, max_length=12)
    birth_date: date
    gender: Optional[GenderEnum]
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    registered_since: Optional[date] = Field(..., default_factory=date.today)
    subscribed_since: Optional[date] = None
    is_subscribed: Optional[bool] = False
    profile_picture_url: Optional[HttpUrl] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, email: EmailStr):
        """
        Validates the email attribute.
        """
        try:
            validate_email(email)
        except EmailNotValidError as e:
            raise ValueError("Invalid email.") from e
        return email

    @field_validator('rut')
    @classmethod
    def validate_rut(cls, rut: str):
        """
        Validates the rut attribute.
        """
        validate_rut(rut)
        return rut

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, phone: str):
        """
        Validates the phone attribute.
        """
        validate_chilean_phone_number(phone)
        return phone

    @field_serializer('profile_picture_url')
    def serialize_profile_picture_url(
            self, profile_picture_url: HttpUrl, _info):
        """
        Serializes the profile_picture_url attribute into a string.
        """
        if profile_picture_url is None:
            return None
        return str(profile_picture_url)

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, birth_date: date):
        """
        Validates the birth_date attribute.
        """
        if birth_date > date.today() - relativedelta(years=18):
            raise ValueError("birth_date must be at least 18 years ago.")
        return birth_date


class UserCreate(UserBase):
    """
    Schema for creating a user.
    """
    password: str = Field(..., min_length=8, max_length=50)

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str):
        """
        Validates the password attribute.
        """
        if not re.match(PASS_REGEX_PATTERN, password):
            raise ValueError(
                "Password must contain at least one lowercase letter, "
                "one uppercase letter, one digit, and one special character."
            )
        return password


class User(UserBase):
    """
    Schema for the User model.
    """
    model_config: ConfigDict = ConfigDict(
        from_attributes=True
    )
    id: int = Field(..., gt=0)


class AdminBase(BaseModel):
    """
    Base schema for the Admin model.
    """
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=50)


class AdminCreate(AdminBase):
    """
    Schema for creating an admin.
    """
    password: str = Field(..., min_length=8, max_length=50)

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str):
        """
        Validates the password attribute.
        """
        if not re.match(PASS_REGEX_PATTERN, password):
            raise ValueError(
                "Password must contain at least one lowercase letter, "
                "one uppercase letter, one digit, and one special character."
            )
        return password


class Admin(AdminBase):
    """
    Schema for the Admin model.
    """
    model_config: ConfigDict = ConfigDict(
        from_attributes=True
    )
    id: int = Field(..., gt=0)
