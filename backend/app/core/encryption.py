"""
Encryption and Decryption Utilities for API Keys

Uses Fernet (symmetric encryption) to encrypt/decrypt sensitive API credentials.
Fernet uses AES 128 in CBC mode with PKCS7 padding.
"""

from cryptography.fernet import Fernet

from app.core.config import settings


def get_encryption_key() -> bytes:
    """
    Get encryption key from settings.

    The key should be a 32 url-safe base64-encoded bytes.
    Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

    Returns:
        Encryption key as bytes
    """
    # SECRET_KEY from settings should be at least 32 characters
    # Fernet requires a 32 url-safe base64-encoded bytes key
    key = settings.SECRET_KEY.encode()

    # If the key is not already a valid Fernet key, derive one
    # In production, use a separate ENCRYPTION_KEY in settings
    if len(key) < 32:
        # Pad the key if it's too short (NOT recommended for production)
        key = key.ljust(32, b"0")

    # Take first 32 bytes and ensure it's url-safe base64
    # For production, use a properly generated Fernet key
    try:
        # Try to use the key directly if it's already valid
        Fernet(key)
        return key
    except Exception:
        # If not valid, use a derived key (simplified approach)
        # In production, use cryptography.hazmat for proper key derivation (PBKDF2, etc.)
        from base64 import urlsafe_b64encode
        import hashlib

        # Derive a proper Fernet key from the secret
        derived = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        return urlsafe_b64encode(derived)


def encrypt_api_key(plain_text: str) -> str:
    """
    Encrypt a plain text API key.

    Args:
        plain_text: Plain text to encrypt

    Returns:
        Encrypted text as base64 string
    """
    if not plain_text:
        return ""

    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plain_text.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_text: str) -> str:
    """
    Decrypt an encrypted API key.

    Args:
        encrypted_text: Encrypted text as base64 string

    Returns:
        Decrypted plain text

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
    """
    if not encrypted_text:
        return ""

    key = get_encryption_key()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_text.encode())
    return decrypted.decode()


def encrypt_api_credentials(api_key: str, api_secret: str) -> tuple[str, str]:
    """
    Encrypt both API key and secret.

    Args:
        api_key: Plain text API key
        api_secret: Plain text API secret

    Returns:
        Tuple of (encrypted_api_key, encrypted_api_secret)
    """
    encrypted_key = encrypt_api_key(api_key)
    encrypted_secret = encrypt_api_key(api_secret)
    return encrypted_key, encrypted_secret


def decrypt_api_credentials(
    encrypted_key: str, encrypted_secret: str
) -> tuple[str, str]:
    """
    Decrypt both API key and secret.

    Args:
        encrypted_key: Encrypted API key
        encrypted_secret: Encrypted API secret

    Returns:
        Tuple of (plain_api_key, plain_api_secret)
    """
    plain_key = decrypt_api_key(encrypted_key)
    plain_secret = decrypt_api_key(encrypted_secret)
    return plain_key, plain_secret
