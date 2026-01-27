import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from dotenv import load_dotenv

from auth import router as auth_router
from notes import router as notes_router
from database import user_collection

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.state.templates = templates

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(auth_router)
app.include_router(notes_router)

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.on_event("startup")
def create_default_admin():
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")

    admin = user_collection.find_one({"email": admin_email})

    if not admin:
        user_collection.insert_one({
            "name": "Admin",
            "email": admin_email,
            "password": pwd.hash(admin_password),
            "role": "admin"
        })


@app.get("/")
def root():
    return RedirectResponse("/login")
