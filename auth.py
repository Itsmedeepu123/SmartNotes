from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext

from database import user_collection

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain, hashed):
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
    if user_collection.find_one({"email": email}):
        return request.app.state.templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already exists"}
        )

    user_collection.insert_one({
        "name": name,
        "email": email,
        "password": pwd.hash(password),
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
            {"request": request, "error": "Invalid credentials"}
        )

    # store session
    request.session["user_email"] = user["email"]
    request.session["role"] = user["role"]

    # redirect based on role
    if user["role"] == "admin":
        return RedirectResponse("/admin/dashboard", status_code=303)
    else:
        return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
