from __future__ import annotations

from fastapi import Header, HTTPException, status


def get_current_user_id(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str:
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return x_user_id
