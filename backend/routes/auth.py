from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from models import SignupRequest, LoginRequest, AuthResponse
from database import get_supabase, get_supabase_admin
from auth import get_current_user

router = APIRouter()


@router.post("/signup", response_model=AuthResponse)
async def signup(body: SignupRequest):
    """
    Create a new user account via Supabase Auth, then initialise their
    user-preferences row. Portfolio starts empty ($0); funds are added via
    POST /portfolio/deposit.
    """
    supabase = get_supabase()
    admin = get_supabase_admin()

    try:
        response = supabase.auth.sign_up({"email": body.email, "password": body.password})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not response.user:
        raise HTTPException(status_code=400, detail="Signup failed — no user returned.")

    user_id = response.user.id

    # Create a default preferences row. Non-fatal if it fails (e.g. email not
    # yet confirmed, or timezone enum mismatch — user can update preferences later).
    try:
        admin.table("user-preferences").insert({
            "id": user_id,
            "enable_notification": True,
            "enable_darkmode": False,
            "device_type": "DESKTOP",
            "timezone": "UTC",
        }).execute()
    except Exception:
        pass

    if not response.session:
        # Email confirmation is enabled — account created but no session yet.
        return JSONResponse(
            status_code=202,
            content={"message": "Account created. Please verify your email before logging in."},
        )

    return AuthResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        user_id=user_id,
        email=response.user.email,
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest):
    """Authenticate with email + password and return JWT session tokens."""
    supabase = get_supabase()

    try:
        response = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not response.session:
        raise HTTPException(status_code=401, detail="Login failed — no session returned.")

    return AuthResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        user_id=response.user.id,
        email=response.user.email,
    )


@router.post("/logout")
async def logout(current=Depends(get_current_user)):
    """Invalidate the current session."""
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    return {"message": "Logged out successfully."}


@router.get("/me")
async def me(current=Depends(get_current_user)):
    """Return the authenticated user's basic profile."""
    user = current["user"]
    return {
        "user_id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }
