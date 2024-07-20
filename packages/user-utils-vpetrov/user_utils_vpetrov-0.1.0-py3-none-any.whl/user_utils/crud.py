"""
Recurrent CRUD functions for apps that use the user model.
"""
from typing import Optional
from sqlalchemy.orm import Session

from . import models


def get_user_by_email_if_exists(
        db: Session, email: str) -> Optional[models.User]:
    """
    Returns a user by email if it exists.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_admin_by_email_if_exists(
        db: Session, email: str) -> Optional[models.Admin]:
    """
    Returns an admin by email if it exists.
    """
    return db.query(models.Admin).filter(models.Admin.email == email).first()
