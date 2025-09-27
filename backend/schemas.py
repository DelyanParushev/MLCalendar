from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Event schemas
class ParseRequest(BaseModel):
    text: str

class ParseResult(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None

class EventCreate(BaseModel):
    title: str
    start: datetime
    end: Optional[datetime] = None
    raw_text: Optional[str] = None

class EventOut(BaseModel):
    id: int
    title: str
    start: datetime
    end: Optional[datetime] = None
    raw_text: Optional[str] = None
    owner_id: int

    model_config = {"from_attributes": True}