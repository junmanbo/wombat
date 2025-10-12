"""
CRUD operations for User API Keys
"""

import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.encryption import decrypt_api_credentials, encrypt_api_credentials
from app.models.user_api_keys import UserApiKey, UserApiKeyCreate, UserApiKeyUpdate


def create_user_api_key(
    *, session: Session, user_id: uuid.UUID, api_key_create: UserApiKeyCreate
) -> UserApiKey:
    """
    Create a new API key for a user.

    Encrypts the API key and secret before storing.

    Args:
        session: Database session
        user_id: User ID
        api_key_create: API key data with plain text credentials

    Returns:
        Created UserApiKey instance
    """
    # Encrypt API credentials
    encrypted_key, encrypted_secret = encrypt_api_credentials(
        api_key_create.encrypted_api_key,  # Plain text from input
        api_key_create.encrypted_api_secret,  # Plain text from input
    )

    # Create database object with encrypted credentials
    db_obj = UserApiKey(
        user_id=user_id,
        exchange_type=api_key_create.exchange_type,
        encrypted_api_key=encrypted_key,
        encrypted_api_secret=encrypted_secret,
        account_number=api_key_create.account_number,
        is_demo=api_key_create.is_demo,
        is_active=api_key_create.is_active,
        nickname=api_key_create.nickname,
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_user_api_key(*, session: Session, api_key_id: int) -> UserApiKey | None:
    """
    Get an API key by ID.

    Args:
        session: Database session
        api_key_id: API key ID

    Returns:
        UserApiKey instance or None if not found
    """
    statement = select(UserApiKey).where(UserApiKey.id == api_key_id)
    return session.exec(statement).first()


def get_user_api_keys(
    *, session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[UserApiKey]:
    """
    Get all API keys for a user.

    Args:
        session: Database session
        user_id: User ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of UserApiKey instances
    """
    statement = (
        select(UserApiKey)
        .where(UserApiKey.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(UserApiKey.created_at.desc())
    )
    return list(session.exec(statement).all())


def get_user_api_key_by_exchange(
    *,
    session: Session,
    user_id: uuid.UUID,
    exchange_type: str,
    is_demo: bool = False,
) -> UserApiKey | None:
    """
    Get active API key for a specific exchange.

    Args:
        session: Database session
        user_id: User ID
        exchange_type: Exchange type (e.g., 'KIS', 'UPBIT')
        is_demo: Whether to get demo or production key

    Returns:
        UserApiKey instance or None if not found
    """
    statement = select(UserApiKey).where(
        UserApiKey.user_id == user_id,
        UserApiKey.exchange_type == exchange_type,
        UserApiKey.is_demo == is_demo,
        UserApiKey.is_active == True,
    )
    return session.exec(statement).first()


def get_decrypted_api_key(
    *, session: Session, api_key_id: int
) -> tuple[str, str] | None:
    """
    Get decrypted API credentials.

    SECURITY WARNING: Use this function carefully and only when necessary.
    Never return decrypted credentials in API responses.

    Args:
        session: Database session
        api_key_id: API key ID

    Returns:
        Tuple of (api_key, api_secret) or None if not found
    """
    api_key = get_user_api_key(session=session, api_key_id=api_key_id)

    if not api_key:
        return None

    try:
        plain_key, plain_secret = decrypt_api_credentials(
            api_key.encrypted_api_key, api_key.encrypted_api_secret
        )
        return plain_key, plain_secret
    except Exception as e:
        print(f"Error decrypting API key {api_key_id}: {e}")
        return None


def get_decrypted_api_key_by_exchange(
    *,
    session: Session,
    user_id: uuid.UUID,
    exchange_type: str,
    is_demo: bool = False,
) -> tuple[str, str, str | None] | None:
    """
    Get decrypted API credentials for a specific exchange.

    SECURITY WARNING: Use this function carefully and only when necessary.
    Never return decrypted credentials in API responses.

    Args:
        session: Database session
        user_id: User ID
        exchange_type: Exchange type (e.g., 'KIS', 'UPBIT')
        is_demo: Whether to get demo or production key

    Returns:
        Tuple of (api_key, api_secret, account_number) or None if not found
    """
    api_key = get_user_api_key_by_exchange(
        session=session, user_id=user_id, exchange_type=exchange_type, is_demo=is_demo
    )

    if not api_key:
        return None

    try:
        plain_key, plain_secret = decrypt_api_credentials(
            api_key.encrypted_api_key, api_key.encrypted_api_secret
        )
        return plain_key, plain_secret, api_key.account_number
    except Exception as e:
        print(f"Error decrypting API key for {exchange_type}: {e}")
        return None


def update_user_api_key(
    *, session: Session, db_api_key: UserApiKey, api_key_in: UserApiKeyUpdate
) -> Any:
    """
    Update an API key.

    If encrypted fields are provided, they will be re-encrypted.

    Args:
        session: Database session
        db_api_key: Existing UserApiKey instance
        api_key_in: Update data

    Returns:
        Updated UserApiKey instance
    """
    api_key_data = api_key_in.model_dump(exclude_unset=True)

    # If API credentials are being updated, encrypt them
    if "encrypted_api_key" in api_key_data and "encrypted_api_secret" in api_key_data:
        encrypted_key, encrypted_secret = encrypt_api_credentials(
            api_key_data["encrypted_api_key"],  # Plain text from input
            api_key_data["encrypted_api_secret"],  # Plain text from input
        )
        api_key_data["encrypted_api_key"] = encrypted_key
        api_key_data["encrypted_api_secret"] = encrypted_secret
    elif "encrypted_api_key" in api_key_data:
        # Only key is being updated
        encrypted_key = encrypt_api_credentials(
            api_key_data["encrypted_api_key"], ""
        )[0]
        api_key_data["encrypted_api_key"] = encrypted_key
    elif "encrypted_api_secret" in api_key_data:
        # Only secret is being updated
        encrypted_secret = encrypt_api_credentials(
            "", api_key_data["encrypted_api_secret"]
        )[1]
        api_key_data["encrypted_api_secret"] = encrypted_secret

    # Update timestamp
    from datetime import datetime, timezone

    api_key_data["updated_at"] = datetime.now(timezone.utc)

    db_api_key.sqlmodel_update(api_key_data)
    session.add(db_api_key)
    session.commit()
    session.refresh(db_api_key)
    return db_api_key


def delete_user_api_key(*, session: Session, api_key_id: int) -> bool:
    """
    Delete an API key.

    Args:
        session: Database session
        api_key_id: API key ID

    Returns:
        True if deleted, False if not found
    """
    api_key = get_user_api_key(session=session, api_key_id=api_key_id)
    if api_key:
        session.delete(api_key)
        session.commit()
        return True
    return False


def deactivate_user_api_key(*, session: Session, api_key_id: int) -> UserApiKey | None:
    """
    Deactivate an API key (soft delete).

    Args:
        session: Database session
        api_key_id: API key ID

    Returns:
        Updated UserApiKey instance or None if not found
    """
    api_key = get_user_api_key(session=session, api_key_id=api_key_id)
    if api_key:
        api_key.is_active = False

        from datetime import datetime, timezone

        api_key.updated_at = datetime.now(timezone.utc)

        session.add(api_key)
        session.commit()
        session.refresh(api_key)
        return api_key
    return None
