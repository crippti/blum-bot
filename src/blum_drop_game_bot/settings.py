import re
from typing import List, Optional

from pydantic import BaseModel, field_validator

class TgConnection(BaseModel):
    proxy: Optional[str] = None
    jwt_token: str

    @field_validator('jwt_token')
    @classmethod
    def start_with_bearer(cls, v: str):
        if not v.startswith('Bearer '):
            raise ValueError('JWT token must start with "Bearer ".')
        return v

    @field_validator('proxy')
    @classmethod
    def start_with_bearer(cls, v: str):
        if not re.match(r'https?:\/\/.+:.+@.+:.+', v):
            raise ValueError('Proxy must be in format http://user:password@host:port.')
        return v

class ThreadSettings(BaseModel):
    points: int
    tg: TgConnection

    @field_validator('points')
    @classmethod
    def start_with_bearer(cls, v: int):
        if v > 270:
            raise ValueError('Points must be less than 270.')
        return v




class Settings(BaseModel):
    telegrams: List[TgConnection]
    min_points: int
    max_points: int

    cpu_count: Optional[int] = None

    @field_validator('max_points')
    @classmethod
    def start_with_bearer(cls, v: int):
        if v > 270:
            raise ValueError('Points must be less than 270.')
        return v

