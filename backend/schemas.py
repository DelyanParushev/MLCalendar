from pydantic import BaseModel, EmailStr, field_serializer
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
    profile_picture: Optional[str] = None

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
    
    @field_serializer('start', 'end')
    def serialize_datetime(self, dt: Optional[datetime], _info):
        if dt is None:
            return None
        # Return datetime without timezone info (naive datetime string)
        # If dt has timezone, convert to naive by removing tzinfo
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt.isoformat()