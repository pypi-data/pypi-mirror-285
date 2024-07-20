"""
User models.
"""
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import Column, Integer, Boolean, String, Date,\
    Enum, DateTime, ForeignKey
from sqlalchemy.orm import validates, relationship
from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext

from .validators import validate_chilean_phone_number, validate_rut
from .schemas import GenderEnum
from .database import Base


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    User model.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String(15), nullable=False)
    rut = Column(String(12), unique=True, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=True, default=None)
    region = Column(String(50), nullable=True, default=None)
    city = Column(String(50), nullable=True, default=None)
    address = Column(String(100), nullable=True, default=None)
    registered_since = Column(Date, nullable=False)
    subscribed_since = Column(Date, nullable=True, default=None)
    is_subscribed = Column(Boolean, nullable=False, default=False)
    profile_picture_url = Column(String, nullable=True, default=None)

    @validates("name")
    def validate_name(self, _, name):
        """
        Validates the name attribute.
        """
        if not name:
            raise ValueError("name must not be empty.")
        return name

    @validates("last_name")
    def validate_last_name(self, _, last_name):
        """
        Validates the last_name attribute.
        """
        if not last_name:
            raise ValueError("last_name must not be empty.")
        return last_name

    @validates("email")
    def validate_email(self, _, email):
        """
        Validates the email attribute.
        """
        try:
            validate_email(email, check_deliverability=True)
        except EmailNotValidError as e:
            raise ValueError("email must not be empty.") from e
        return email

    @validates("phone")
    def validate_phone_is_chilean_phone(self, _, phone):
        """
        Validates the phone attribute.
        """
        validate_chilean_phone_number(phone)
        return phone

    @validates("rut")
    def validate_rut_input(self, _, rut):
        """
        Validates the rut attribute.
        """
        validate_rut(rut)
        return rut

    @validates("birth_date")
    def validate_birth_date(self, _, birth_date):
        """
        Validates the birth_date attribute.
        """
        if birth_date > date.today() - relativedelta(years=18):
            raise ValueError("birth_date must be at least 18 years ago.")
        return birth_date

    def verify_password(self, password: str) -> bool:
        """
        Verifies the user's password.
        """
        return pwd_context.verify(password, self.hashed_password)

    @classmethod
    def get_hashed_password(cls, password: str):
        """
        Returns the hashed password.
        """
        return pwd_context.hash(password)


class Admin(Base):
    """
    Admin model.
    """
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    hashed_password = Column(String, nullable=False)

    two_factor = relationship(
        "TwoFactor", back_populates="admin", uselist=False,
        cascade="all, delete-orphan")

    @validates("email")
    def validate_email(self, _, email):
        """
        Validates the email attribute.
        """
        try:
            validate_email(email, check_deliverability=True)
        except EmailNotValidError as e:
            raise ValueError("email must not be empty.") from e
        return email

    @validates("name")
    def validate_name(self, _, name):
        """
        Validates the name attribute.
        """
        if not name:
            raise ValueError("name must not be empty.")
        return name

    def verify_password(self, password: str) -> bool:
        """
        Verifies the user's password.
        """
        return pwd_context.verify(password, self.hashed_password)

    @classmethod
    def get_hashed_password(cls, password: str):
        """
        Returns the hashed password.
        """
        return pwd_context.hash(password)


class TwoFactor(Base):
    """
    Two factor model.
    """
    __tablename__ = "two_factors"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(
        Integer, ForeignKey("admins.id"),
        nullable=False, unique=True, index=True)
    token = Column(String, nullable=False, unique=True)
    validation_code = Column(String(6), nullable=False)
    expiration_time = Column(DateTime, nullable=False)
    confirmed = Column(Boolean, nullable=False, default=False)

    admin = relationship(
        "Admin", back_populates="two_factor",
        uselist=False, foreign_keys=[admin_id])

    @validates("admin_id")
    def validate_admin_id(self, _, admin_id):
        """
        Validates the admin_id attribute.
        """
        if not admin_id:
            raise ValueError("admin_id must not be empty.")
        return admin_id

    @validates("token")
    def validate_token(self, _, token):
        """
        Validates the token attribute.
        """
        if not token:
            raise ValueError("token must not be empty.")
        return token
