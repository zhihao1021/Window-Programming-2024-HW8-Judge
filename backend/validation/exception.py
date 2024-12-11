from fastapi import status
from fastapi.exceptions import HTTPException

AUTHORIZE_FAILED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Authorized failed"
)

TOKEN_EXPIRED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The token is expired"
)

INVALIDE_AUTHENTICATION_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials"
)
