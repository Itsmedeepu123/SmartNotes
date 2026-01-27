from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from bson import ObjectId
from datetime import datetime
from pymongo import ReturnDocument

from database import note_collection, user_collection, counter_collection

router = APIRouter()


def get_current_user(request: Request):
    email = request.session.get("user_email")
    if not email:
        return None
    return user_collection.find_one({"email": email})


def get_next_note_no(user_email: str) -> int:
    # ✅ atomic counter per user (no duplicates)
    doc = counter_collection.find_one_and_update(
        {"_id": f"note_no:{user_email}"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return doc["seq"]


@router.get("/dashboard")
def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    notes = list(note_collection.find({"user_email": user["email"]}).sort("note_no", -1))

    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "notes": notes}
    )


# ✅ when user clicks "Add Note" button, keep them on dashboard
@router.get("/add-note")
def add_note_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return RedirectResponse("/dashboard#add-form", status_code=303)


@router.post("/add-note")
def add_note(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    category: str = Form("")
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    tags_list = [t.strip() for t in tags.split(",") if t.strip()]

    note_collection.insert_one({
        "user_email": user["email"],
        "note_no": get_next_note_no(user["email"]),   # ✅ serial ID
        "title": title,
        "content": content,
        "tags": tags_list,
        "category": category.strip(),
        "created_at": datetime.utcnow()
    })

    return RedirectResponse("/dashboard", status_code=303)


@router.get("/edit-note/{note_id}")
def edit_note_page(request: Request, note_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    note = note_collection.find_one({"_id": ObjectId(note_id), "user_email": user["email"]})
    if not note:
        return RedirectResponse("/dashboard", status_code=303)

    return request.app.state.templates.TemplateResponse(
        "edit_note.html",
        {"request": request, "note": note}
    )


@router.post("/edit-note/{note_id}")
def edit_note(
    request: Request,
    note_id: str,
    title: str = Form(...),
    content: str = Form(...),
    tags: str = Form(""),
    category: str = Form("")
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    tags_list = [t.strip() for t in tags.split(",") if t.strip()]

    note_collection.update_one(
        {"_id": ObjectId(note_id), "user_email": user["email"]},
        {"$set": {"title": title, "content": content, "tags": tags_list, "category": category.strip()}}
    )
    return RedirectResponse("/dashboard", status_code=303)


@router.post("/delete-note/{note_id}")
def delete_note(request: Request, note_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)

    note_collection.delete_one({"_id": ObjectId(note_id), "user_email": user["email"]})
    return RedirectResponse("/dashboard", status_code=303)
