from fastapi import APIRouter, Body, status

from validation import JWTManager, JWT

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=JWT
)
def login(
    sid: str = Body(embed=True),
    password: str = Body(embed=True)
) -> JWT:
    return JWTManager.login(
        sid=sid,
        password=password
    )
