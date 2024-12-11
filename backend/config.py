from orjson import dumps, loads, OPT_INDENT_2
from pydantic import BaseModel

from os import urandom


class Config(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    sql_server: str = "127.0.0.1"
    jwt_key: str = urandom(16).hex()


try:
    with open("config.json", "rb") as config_file:
        config = Config(**loads(config_file.read()))
except:
    with open("config.json", "wb") as config_file:
        config_file.write(dumps(
            Config().model_dump(),
            option=OPT_INDENT_2
        ))
    print("Please go to modify your config file")
    exit(0)

HOST = config.host
PORT = config.port
SQL_SERVER = config.sql_server
JWT_KEY = config.jwt_key
