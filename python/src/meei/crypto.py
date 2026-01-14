"""
加密模組 - AES-256 加密 API keys
"""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MEEI_DIR = Path.home() / ".meei"
KEY_FILE = MEEI_DIR / ".key"
SALT_FILE = MEEI_DIR / ".salt"


def _ensure_dir():
    """確保 ~/.meei 目錄存在且權限正確"""
    MEEI_DIR.mkdir(exist_ok=True)
    # Windows 不支援 chmod，但在 Unix 上設定 700
    if os.name != "nt":
        os.chmod(MEEI_DIR, 0o700)


def _derive_key(password: str, salt: bytes) -> bytes:
    """從密碼衍生加密金鑰"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def init_encryption(password: str) -> bool:
    """初始化加密系統"""
    _ensure_dir()

    salt = os.urandom(16)
    SALT_FILE.write_bytes(salt)

    key = _derive_key(password, salt)
    KEY_FILE.write_bytes(key)

    # 設定檔案權限
    if os.name != "nt":
        os.chmod(KEY_FILE, 0o600)
        os.chmod(SALT_FILE, 0o600)

    return True


def is_initialized() -> bool:
    """檢查是否已初始化"""
    return KEY_FILE.exists() and SALT_FILE.exists()


def get_fernet(password: str = None) -> Fernet:
    """取得 Fernet 加密器"""
    if not is_initialized():
        raise RuntimeError("meei 尚未初始化，請執行 `meei init`")

    if password:
        salt = SALT_FILE.read_bytes()
        key = _derive_key(password, salt)
    else:
        key = KEY_FILE.read_bytes()

    return Fernet(key)


def encrypt(data: str, password: str = None) -> str:
    """加密字串"""
    f = get_fernet(password)
    return f.encrypt(data.encode()).decode()


def decrypt(data: str, password: str = None) -> str:
    """解密字串"""
    f = get_fernet(password)
    return f.decrypt(data.encode()).decode()
