"""
API routes for User API Keys management
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.crud import user_api_keys as crud_api_keys
from app.models.user_api_keys import (
    UserApiKey,
    UserApiKeyCreate,
    UserApiKeyPublic,
    UserApiKeysPublic,
    UserApiKeyUpdate,
)
from app.models.users import Message

router = APIRouter(prefix="/user-api-keys", tags=["user-api-keys"])


@router.get("/", response_model=UserApiKeysPublic)
def read_user_api_keys(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve current user's API keys.

    Returns list of API keys WITHOUT decrypted credentials.
    """
    count_statement = (
        select(func.count()).select_from(UserApiKey).where(UserApiKey.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    api_keys = crud_api_keys.get_user_api_keys(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )

    return {"data": api_keys, "count": count}


@router.get("/exchange/{exchange_type}", response_model=UserApiKeyPublic)
def read_user_api_key_by_exchange(
    exchange_type: str,
    session: SessionDep,
    current_user: CurrentUser,
    is_demo: bool = False,
) -> Any:
    """
    Get current user's active API key for a specific exchange.

    Args:
        exchange_type: Exchange type (e.g., 'KIS', 'UPBIT')
        is_demo: Whether to get demo or production key (default: False)

    Returns:
        API key WITHOUT decrypted credentials
    """
    api_key = crud_api_keys.get_user_api_key_by_exchange(
        session=session,
        user_id=current_user.id,
        exchange_type=exchange_type.upper(),
        is_demo=is_demo,
    )

    if not api_key:
        raise HTTPException(
            status_code=404,
            detail=f"No active API key found for exchange '{exchange_type}' (is_demo={is_demo})",
        )

    return api_key


@router.post("/", response_model=UserApiKeyPublic)
def create_user_api_key(
    *, session: SessionDep, current_user: CurrentUser, api_key_in: UserApiKeyCreate
) -> Any:
    """
    Create a new API key for the current user.

    IMPORTANT: Send plain text API key and secret in the request.
    They will be encrypted before storage.

    Request body example:
    ```json
    {
        "exchange_type": "KIS",
        "encrypted_api_key": "plain_api_key_here",
        "encrypted_api_secret": "plain_api_secret_here",
        "account_number": "12345678",
        "is_demo": true,
        "nickname": "My Demo Account"
    }
    ```

    Note: Despite the field names, send PLAIN TEXT credentials.
    The encryption happens server-side.
    """
    # Normalize exchange type to uppercase
    api_key_in.exchange_type = api_key_in.exchange_type.upper()

    # Check if user already has an active key for this exchange/demo combination
    existing_key = crud_api_keys.get_user_api_key_by_exchange(
        session=session,
        user_id=current_user.id,
        exchange_type=api_key_in.exchange_type,
        is_demo=api_key_in.is_demo,
    )

    if existing_key:
        raise HTTPException(
            status_code=400,
            detail=(
                f"You already have an active API key for {api_key_in.exchange_type} "
                f"({'demo' if api_key_in.is_demo else 'production'}). "
                f"Please deactivate or delete the existing key first."
            ),
        )

    # Validate credentials are provided
    if not api_key_in.encrypted_api_key or not api_key_in.encrypted_api_secret:
        raise HTTPException(
            status_code=400,
            detail="Both API key and API secret are required",
        )

    api_key = crud_api_keys.create_user_api_key(
        session=session, user_id=current_user.id, api_key_create=api_key_in
    )

    return api_key


@router.get("/{api_key_id}", response_model=UserApiKeyPublic)
def read_user_api_key_by_id(
    api_key_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific API key by ID.

    Returns API key WITHOUT decrypted credentials.
    Only the owner can access their own keys.
    """
    api_key = crud_api_keys.get_user_api_key(session=session, api_key_id=api_key_id)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Check ownership
    if api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this API key"
        )

    return api_key


@router.patch("/{api_key_id}", response_model=UserApiKeyPublic)
def update_user_api_key(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    api_key_id: int,
    api_key_in: UserApiKeyUpdate,
) -> Any:
    """
    Update an API key.

    Can update:
    - API credentials (will be re-encrypted)
    - Account number
    - Nickname
    - is_demo flag
    - is_active flag

    IMPORTANT: If updating credentials, send plain text.
    They will be encrypted before storage.
    """
    db_api_key = crud_api_keys.get_user_api_key(session=session, api_key_id=api_key_id)

    if not db_api_key:
        raise HTTPException(
            status_code=404,
            detail="The API key with this id does not exist in the system",
        )

    # Check ownership
    if db_api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this API key"
        )

    # If changing exchange type or is_demo, check for conflicts
    if api_key_in.exchange_type or api_key_in.is_demo is not None:
        check_exchange = api_key_in.exchange_type or db_api_key.exchange_type
        check_is_demo = (
            api_key_in.is_demo if api_key_in.is_demo is not None else db_api_key.is_demo
        )

        existing_key = crud_api_keys.get_user_api_key_by_exchange(
            session=session,
            user_id=current_user.id,
            exchange_type=check_exchange,
            is_demo=check_is_demo,
        )

        if existing_key and existing_key.id != api_key_id:
            raise HTTPException(
                status_code=409,
                detail="Another active API key already exists for this exchange/demo combination",
            )

    db_api_key = crud_api_keys.update_user_api_key(
        session=session, db_api_key=db_api_key, api_key_in=api_key_in
    )

    return db_api_key


@router.post("/{api_key_id}/deactivate", response_model=UserApiKeyPublic)
def deactivate_user_api_key(
    api_key_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Deactivate an API key (soft delete).

    Deactivated keys are kept in the database but cannot be used.
    """
    db_api_key = crud_api_keys.get_user_api_key(session=session, api_key_id=api_key_id)

    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Check ownership
    if db_api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to deactivate this API key"
        )

    if not db_api_key.is_active:
        raise HTTPException(status_code=400, detail="API key is already deactivated")

    deactivated_key = crud_api_keys.deactivate_user_api_key(
        session=session, api_key_id=api_key_id
    )

    if not deactivated_key:
        raise HTTPException(status_code=500, detail="Failed to deactivate API key")

    return deactivated_key


@router.delete("/{api_key_id}")
def delete_user_api_key(
    api_key_id: int, session: SessionDep, current_user: CurrentUser
) -> Message:
    """
    Permanently delete an API key.

    WARNING: This action cannot be undone.
    Consider using the deactivate endpoint instead.
    """
    db_api_key = crud_api_keys.get_user_api_key(session=session, api_key_id=api_key_id)

    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Check ownership
    if db_api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this API key"
        )

    success = crud_api_keys.delete_user_api_key(session=session, api_key_id=api_key_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete API key")

    return Message(message="API key deleted successfully")
