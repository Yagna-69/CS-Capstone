from fastapi import APIRouter, HTTPException, Depends
from models import PreferencesUpdate
from database import get_supabase_admin
from auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_preferences(current=Depends(get_current_user)):
    """Return the authenticated user's preferences."""
    user_id = current["user"].id
    admin = get_supabase_admin()

    try:
        resp = admin.table("user-preferences").select("*").eq("id", user_id).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if not resp.data:
        raise HTTPException(status_code=404, detail="Preferences not found.")

    return resp.data[0]


@router.put("/")
async def update_preferences(body: PreferencesUpdate, current=Depends(get_current_user)):
    """Update one or more preference fields for the authenticated user."""
    user_id = current["user"].id
    admin = get_supabase_admin()

    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    try:
        resp = admin.table("user-preferences").update(updates).eq("id", user_id).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if not resp.data:
        raise HTTPException(status_code=404, detail="Preferences not found — was the account created correctly?")

    return resp.data[0]
