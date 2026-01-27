from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext

from database import user_collection

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd.verify(plain, hashed)


@router.get("/register")
def register_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@router.post("/register")
def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    old = user_collection.find_one({"email": email})
    if old:
        return request.app.state.templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already exists"}
        )

    user_collection.insert_one({
        "name": name,
        "email": email,
        "password": hash_password(password),
        "role": "user"
    })

    return RedirectResponse("/login", status_code=303)


@router.get("/login")
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    user = user_collection.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"}
        )

    # session
    request.session["user_email"] = user["email"]
    request.session["role"] = user.get("role", "user")

    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
