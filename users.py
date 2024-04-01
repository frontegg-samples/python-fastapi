from pydantic import BaseModel


class SystemUser(BaseModel):
    id: str
    name: str
    email: str
