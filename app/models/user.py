from pydantic import Field, field_validator
from typing import ClassVar
import re
from .base import BaseFirestoreModel

class User(BaseFirestoreModel):
    COLLECTION_NAME: ClassVar[str] = "users"
    
    phone: str = Field(..., description="User's phone number")
    preferred_language: str = Field(default="ur", description="Preferred language code (e.g., ur, en)")

    @field_validator('phone')
    @classmethod
    def validate_pakistani_phone(cls, v: str) -> str:
        # Validates standard Pakistani mobile format like +923001234567 or 03001234567
        pattern = r"^(?:\+92|0)3[0-4][0-9]{8}$"
        if not re.match(pattern, v):
            raise ValueError('Invalid Pakistani phone number format')
        return v
