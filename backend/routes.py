from fastapi import APIRouter, HTTPException
from database import get_supabase

api_router = APIRouter()

@api_router.get("/items")
async def get_items():
    try:
        supabase = get_supabase()
        response = supabase.table("items").select("*").execute()
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/items/{item_id}")
async def get_item(item_id: int):
    try:
        supabase = get_supabase()
        response = supabase.table("items").select("*").eq("id", item_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"data": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/items")
async def create_item(item: dict):
    try:
        supabase = get_supabase()
        response = supabase.table("items").insert(item).execute()
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
