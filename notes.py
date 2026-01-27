from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from bson import ObjectId
from datetime import datetime

from database import user_collection, note_collection

router = APIRouter()


# ------------get logged-in user-----------------
def get_user(request: Request):
    email = request.session.get("user_email")
    role = request.session.get("role")

    if not email:
        return None, None

    user = user_collection.find_one({"email": email})
    return user, role


# ---------------USER DASHBOARD---------------
@router.get("/dashboard")
def dashboard(request: Request):
    user, role = get_user(request)

    if not user or role != "user":
        return RedirectResponse("/login", status_code=303)

    notes = list(note_collection.find({"user_email": user["email"]}))

    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "notes": notes}
    )


# -----------------ADD NOTE (POST)-----------
@router.post("/add-note")
def add_note(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    category: str = Form("")
):
    user, role = get_user(request)

    if not user or role != "user":
        return RedirectResponse("/login", status_code=303)

    # simple ID logic
    total_notes = note_collection.count_documents({"user_email": user["email"]})
    note_id = total_notes + 1

    tags_list = tags.split(",") if tags else []

    note_collection.insert_one({
        "user_email": user["email"],
        "note_no": note_id,
        "title": title,
        "content": content,
        "tags": tags_list,
        "category": category,
        "created_at": datetime.now().strftime("%d-%m-%Y %H:%M")
    })

    return RedirectResponse("/dashboard", status_code=303)


# --------------------EDIT NOTE PAGE-------------------------
@router.get("/edit-note/{note_id}")
def edit_note_page(request: Request, note_id: str):
    user, role = get_user(request)

    if not user or role != "user":
        return RedirectResponse("/login", status_code=303)

    note = note_collection.find_one({"_id": ObjectId(note_id)})

    return request.app.state.templates.TemplateResponse(
        "edit_note.html",
        {"request": request, "note": note}
    )


# --------------UPDATE NOTE-----------------
@router.post("/edit-note/{note_id}")
def update_note(
    request: Request,
    note_id: str,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    category: str = Form("")
):
    user, role = get_user(request)

    if not user or role != "user":
        return RedirectResponse("/login", status_code=303)

    tags_list = tags.split(",") if tags else []

    note_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {
            "title": title,
            "content": content,
            "tags": tags_list,
            "category": category
        }}
    )

    return RedirectResponse("/dashboard", status_code=303)


# --------------------DELETE NOTE--------------------
@router.post("/delete-note/{note_id}")
def delete_note(request: Request, note_id: str):
    user, role = get_user(request)

    if not user or role != "user":
        return RedirectResponse("/login", status_code=303)

    note_collection.delete_one({"_id": ObjectId(note_id)})

    return RedirectResponse("/dashboard", status_code=303)


#------------------ ADMIN DASHBOARD-----------------------
@router.get("/admin/dashboard")
def admin_dashboard(request: Request):
    role = request.session.get("role")

    if role != "admin":
        return RedirectResponse("/login", status_code=303)

    users = list(user_collection.find())
    notes = list(note_collection.find())

    return request.app.state.templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "users": users, "notes": notes}
    )
