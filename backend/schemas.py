from pydantic import BaseModel

class User(BaseModel):
    username: str

class UserWithPassword(User):
    password: str
