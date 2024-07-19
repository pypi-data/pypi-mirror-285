# modelss/user.py

from pydantic import BaseModel, SecretStr

class User(BaseModel):
    name: str
    username: str
    password: SecretStr

class Login(BaseModel):
    username:  str
    password: SecretStr
    verification: str

