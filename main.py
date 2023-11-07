from fastapi import FastAPI, Form, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse
from uuid import uuid4

# FastAPI application
app = FastAPI()

# PostgreSQL database connection
DATABASE_URL = "postgresql://username:password@localhost/database"
pg_db = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy models
Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    user_id = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)

class Profile(Base):
    __tablename__ = "Profile"
    user_id = Column(String, ForeignKey("Users.user_id"), primary_key=True, index=True)
    profile_picture = Column(String)

# Pydantic model for registration
class Registration(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    profile_picture: UploadFile = File(...)

# Registration endpoint
@app.post("/register/")
async def register_user(registration: Registration, request: Request):
    # Check if email and phone already exist in "Users" table
    async with pg_db.transaction():
        query = User.__table__.select().where(User.email == registration.email)
        user = await pg_db.fetch_one(query)
        if user:
            return JSONResponse(content={"message": "Email already exists"}, status_code=400)

        query = User.__table__.select().where(User.phone == registration.phone)
        user = await pg_db.fetch_one(query)
        if user:
            return JSONResponse(content={"message": "Phone already exists"}, status_code=400)

    # Generate a unique user_id
    user_id = str(uuid4())

    # Store user data in "Users" table
    async with pg_db.transaction():
        query = User.__table__.insert().values(
            user_id=user_id,
            first_name=registration.full_name.split()[0],
            email=registration.email,
            phone=registration.phone,
            password=registration.password,
        )
        await pg_db.execute(query)

    # Store profile picture in "Profile" table
    profile_picture_bytes = await registration.profile_picture.read()
    async with pg_db.transaction():
        query = Profile.__table__.insert().values(
            user_id=user_id,
            profile_picture=profile_picture_bytes,
        )
        await pg_db.execute(query)

    return JSONResponse(content={"message": "User registered successfully"})

# GET method for user details
@app.get("/user/{user_id}")
async def get_user_details(user_id: str):
    # Retrieve user details from "Users" table
    async with pg_db.transaction():
        query = User.__table__.select().where(User.user_id == user_id)
        user = await pg_db.fetch_one(query)

    if user:
        # Retrieve profile picture from "Profile" table
        async with pg_db.transaction():
            query = Profile.__table__.select().where(Profile.user_id == user_id)
            profile = await pg_db.fetch_one(query)

        if profile:
            return {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "email": user.email,
                "phone": user.phone,
                "profile_picture": profile.profile_picture
            }
    return JSONResponse(content={"message": "User not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn

    # Set up PostgreSQL database
    pg_db.connect()
    pg_db.execute('''CREATE TABLE IF NOT EXISTS "Users" (
                    user_id UUID PRIMARY KEY,
                    first_name VARCHAR,
                    email VARCHAR UNIQUE,
                    phone VARCHAR,
                    password VARCHAR
                    )''')
    pg_db.execute('''CREATE TABLE IF NOT EXISTS "Profile" (
                    user_id UUID PRIMARY KEY REFERENCES "Users" (user_id),
                    profile_picture BYTEA
                    )''')
    pg_db.disconnect()

    # Start the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8000)
