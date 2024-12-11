from fastapi import APIRouter, Body, Depends, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from pymssql import connect
from pymssql.exceptions import OperationalError, ProgrammingError

from datetime import datetime
from os import makedirs
from os.path import isdir
from typing import Annotated, Optional
from traceback import format_exc

from config import SQL_SERVER
from score_manager import SCORE_MANAGER
from testcase import TESTCASE, Testcase
from validation import JWTDataWithPassword, JWTManager


class CheckResult(BaseModel):
    success: bool = True


UserDepend = Annotated[
    JWTDataWithPassword,
    Depends(JWTManager.validation_function)
]

router = APIRouter(
    prefix="/check",
    tags=["Check"]
)


def dealing_exception(
    user: JWTDataWithPassword,
    query_strings: Optional[list[str]]
):
    if not isdir("error_logs"):
        makedirs("error_logs")
    with open(f"error_logs/{user.username}.log", "a", encoding="utf-8") as error_log:
        error_log.write(f"=========={datetime.now().isoformat()}==========\n")
        if query_strings:
            error_log.write("==========Query String Start==========\n")
            error_log.write("\n".join(query_strings))
            error_log.write("\n==========Query String End==========\n")
        error_log.write(format_exc())
        error_log.write("\n\n")
    raise HTTPException(
        detail=f"Traceback: {format_exc()}",
        status_code=status.HTTP_400_BAD_REQUEST
    )


def check(
    user: JWTDataWithPassword,
    testcase_data: Testcase,
    query_strings: Optional[list[str]] = None,
) -> CheckResult:
    if testcase_data.user_query_string and query_strings is None:
        raise HTTPException(
            detail="Query string not found",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    if testcase_data.user_query_string and len(query_strings) != len(testcase_data.testcases):
        raise HTTPException(
            detail="Query string length error",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        conn = connect(
            server=SQL_SERVER,
            user=user.username,
            password=user.password,
            database=f"{user.username}_db",
            autocommit=True
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'TransactionHistory'
            OR table_name = 'Customers'
            OR table_name = 'Items'
        """)
        if cursor.fetchone()[0] != 3:
            cursor.close()
            conn.close()
            return CheckResult(success=False)

        for i, testcase in enumerate(testcase_data.testcases):
            query_string = query_strings[i] if testcase_data.user_query_string \
                else testcase.query_string

            cursor.execute(
                query_string
            )
            results = cursor.fetchall()

            if set(results) != set(testcase.results):
                cursor.close()
                conn.close()
                return CheckResult(success=False)

        cursor.close()
        conn.close()
        return CheckResult(success=True)
    except ProgrammingError:
        return CheckResult(success=False)
    except OperationalError as exc:
        if len(exc.args) >= 2 and type(exc.args[1]) == str:
            if "incorrect syntax" in exc.args[1].lower():
                return CheckResult(success=False)
        dealing_exception(user=user, query_strings=query_strings)
    except:
        dealing_exception(user=user, query_strings=query_strings)


@router.get(
    path=""
)
def get_scores(
    user: UserDepend
) -> tuple[int, int, int, int]:
    return SCORE_MANAGER.get_scores(user.username)


@router.post(
    path="/{index}",
    status_code=status.HTTP_201_CREATED,
    response_model=CheckResult
)
def check_sub(
    user: UserDepend,
    index: int,
    query_strings: Optional[list[str]] = Body(embed=True, default=None)
) -> CheckResult:
    if index not in range(4):
        raise HTTPException(
            detail="Subtestcase not found",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if SCORE_MANAGER.get_scores(user.username)[index] == 1:
        return CheckResult(success=True)

    result = check(
        user=user,
        testcase_data=TESTCASE[f"testcase_{index + 1}"],
        query_strings=query_strings
    )
    if result.success:
        SCORE_MANAGER.update(user.username, index, 1)
    return result
