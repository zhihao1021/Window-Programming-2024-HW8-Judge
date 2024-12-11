from fastapi import Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import encode, decode
from jwt.exceptions import (
    InvalidTokenError,
    ExpiredSignatureError,
)

from csv import reader
from datetime import datetime, timedelta

from config import JWT_KEY

from .exception import (
    AUTHORIZE_FAILED,
    TOKEN_EXPIRED,
    INVALIDE_AUTHENTICATION_CREDENTIALS,
)
from .schemas import JWT, JWTData, JWTDataWithPassword

try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

SECURITY = Security(HTTPBearer(
    scheme_name="JWT",
))

LOGIN_DATA: dict[str, str] = {}
with open("login.csv", newline="", encoding="utf-8") as login_data:
    LOGIN_DATA.update({
        username.lower(): password.lower()
        for username, password in reader(login_data.readlines())
    })


class JWTManager:
    @staticmethod
    def login(
        sid: str,
        password: str
    ) -> JWT:
        if password != LOGIN_DATA.get(sid):
            raise AUTHORIZE_FAILED

        payload = JWTData(
            username=sid,
            exp=datetime.now(UTC) + timedelta(days=7)
        ).model_dump()

        jwt = encode(
            payload=payload,
            key=JWT_KEY,
            algorithm="HS256",
        )

        return JWT(access_token=jwt)

    @staticmethod
    def validation(
        jwt: str,
    ) -> JWTDataWithPassword:
        try:
            data = decode(
                jwt=jwt,
                key=JWT_KEY,
                algorithms=["HS256"],
                options={
                    "require": ["exp"],
                },
            )
            data = JWTData(**data)
        except ExpiredSignatureError:
            raise TOKEN_EXPIRED
        except InvalidTokenError:
            raise INVALIDE_AUTHENTICATION_CREDENTIALS

        return JWTDataWithPassword(
            **data.model_dump(),
            password=LOGIN_DATA.get(data.username)
        )

    @staticmethod
    def validation_function(
        token: HTTPAuthorizationCredentials = SECURITY,
    ) -> JWTDataWithPassword:
        jwt = token.credentials

        return JWTManager.validation(jwt=jwt)
