from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from models import SignupRequest, LoginRequest, AuthResponse
from database import get_supabase, get_supabase_admin
from auth import get_current_user
from config import settings


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class SendPasswordResetRequest(BaseModel):
    email: str

class ResetPasswordWithTokenRequest(BaseModel):
    access_token: str
    new_password: str

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


@router.post("/change-password")
async def change_password(body: ChangePasswordRequest, current=Depends(get_current_user)):
    """Verify current password then update to new password."""
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    supabase = get_supabase()
    user = current["user"]

    # Verify the current password by attempting a sign-in
    try:
        supabase.auth.sign_in_with_password({"email": user.email, "password": body.current_password})
    except Exception:
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    admin = get_supabase_admin()
    try:
        admin.auth.admin.update_user_by_id(user.id, {"password": body.new_password})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "Password updated successfully."}


@router.post("/send-test-email")
async def send_test_email(current=Depends(get_current_user)):
    """Send a test notification email to the authenticated user via Supabase."""
    user = current["user"]
    admin = get_supabase_admin()
    try:
        # Supabase admin can send a magic-link / OTP style email; for a plain
        # test notification we use generate_link to trigger Supabase's email service.
        admin.auth.admin.generate_link({
            "type": "magiclink",
            "email": user.email,
        })
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": f"Test email sent to {user.email}."}


@router.post("/send-password-reset")
async def send_password_reset(body: SendPasswordResetRequest):
    """Send a Supabase password reset email. Redirects to /reset-password in the frontend."""
    supabase = get_supabase()
    redirect_url = f"{settings.frontend_url}/reset-password"
    try:
        supabase.auth.reset_password_email(body.email, {"redirect_to": redirect_url})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password_with_token(body: ResetPasswordWithTokenRequest):
    """Use the recovery access_token from the reset email to set a new password."""
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    # Exchange the recovery token for a session, then update the password
    supabase = get_supabase()
    try:
        # Set the session using the recovery token so we can call update_user
        session = supabase.auth.set_session(body.access_token, "")
        user_id = session.user.id if session and session.user else None
        if not user_id:
            raise ValueError("Could not resolve user from token.")
    except Exception:
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired.")

    admin = get_supabase_admin()
    try:
        admin.auth.admin.update_user_by_id(user_id, {"password": body.new_password})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "Password updated successfully."}
