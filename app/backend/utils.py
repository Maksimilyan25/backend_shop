from datetime import datetime, timedelta, timezone

import jwt

from .constants import ALGORITHM, SECRET_KEY


async def create_access_token(
        username: str,
        user_id: int,
        is_admin: bool,
        is_supplier: bool,
        is_customer: bool,
        expires_delta: timedelta):
    payload = {
        'sub': username,
        'id': user_id,
        'is_admin': is_admin,
        'is_supplier': is_supplier,
        'is_customer': is_customer,
        'exp': datetime.now(timezone.utc) + expires_delta
    }
    payload['exp'] = int(payload['exp'].timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
