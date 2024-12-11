from pydantic import BaseModel, field_validator

from datetime import datetime
from typing import Union

from schemas import User, UserWithPassword


class JWT(BaseModel):
    token_type: str = "Bearer"
    access_token: str


class JWTData(User):
    exp: datetime

    @field_validator("exp")
    @classmethod
    def datetime_check(cls, v: Union[datetime, int]):
        try:
            return datetime.fromtimestamp(v) if type(v) is not datetime else v
        except:
            raise ValueError


class JWTDataWithPassword(UserWithPassword, JWTData):
    pass
