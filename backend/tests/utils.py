from fastapi import HTTPException


def get_auth_header(access_token: str | None) -> dict[str, str]:
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token")
    return {"Authorization": f"Bearer {access_token}"}
