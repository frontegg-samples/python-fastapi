import uvicorn
from frontegg.fastapi import frontegg
from fastapi import FastAPI, HTTPException, Depends
from frontegg.fastapi.secure_access import FronteggSecurity, User
from starlette.middleware.cors import CORSMiddleware
from users import SystemUser
from typing import List
import os

# frontegg vendor credentials
fe_client_id = os.environ['FRONTEGG_CLIENT']
fe_api_key = os.environ['FRONTEGG_SECRET']

# Temporary in-memory database
users_local_db = []


async def init_frontegg():
    await frontegg.init_app(fe_client_id, fe_api_key)


# Initialize FastAPI app
app = FastAPI()
app.add_event_handler("startup", init_frontegg)
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create routes
@app.get("/users")
async def read_users( _: User = Depends(FronteggSecurity(permissions=["fe.secure.read.users"]))) -> List[SystemUser]:
    return users_local_db


@app.get("/users/{user_id}")
async def read_user(user_id: int, _: User = Depends(FronteggSecurity(permissions=["fe.secure.read.users"]))) -> SystemUser:
    for user in users_local_db:
        if user['id'] == user_id:

            return user

    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users")
async def create_user(system_user: SystemUser, _: User = Depends(FronteggSecurity(permissions=["fe.secure.write.users"]))):
    new_user = SystemUser(
        id=system_user.id,
        email=system_user.email,
        name=system_user.name
    )
    users_local_db.append(new_user.dict())

    return "User successfully created"


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, _: User = Depends(FronteggSecurity(permissions=["fe.secure.delete.users"]))) -> str:
    for i, db_user in enumerate(users_local_db):
        if str(db_user['id']) == str(user_id):
            users_local_db.pop(i)

            return "User successfully deleted"

    raise HTTPException(status_code=404, detail="User not found")


uvicorn.run(app)
