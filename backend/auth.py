from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_supabase

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    FastAPI dependency — validates the Supabase JWT from the Authorization header
    and returns {"user": <GoTrue User>, "access_token": <str>}.
    Inject this into any route that requires authentication.
    """
    token = credentials.credentials
    try:
        response = get_supabase().auth.get_user(token)
        if not response.user:
            raise ValueError("No user returned")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user": response.user, "access_token": token}
