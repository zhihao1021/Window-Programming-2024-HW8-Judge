from orjson import loads
from pydantic import BaseModel, field_validator

from typing import Union


class SubTestcase(BaseModel):
    query_string: str
    results: list[tuple]


class Testcase(BaseModel):
    user_query_string: bool
    testcases: list[SubTestcase]


TESTCASE: dict[str, Testcase] = {}
with open("testcase.json", "rb") as testcase_file:
    raw_data: dict = loads(testcase_file.read())
    TESTCASE.update({
        key: Testcase(**value)
        for key, value in raw_data.items()
    })
