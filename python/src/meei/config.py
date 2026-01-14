"""
設定管理模組 - 加密儲存 API keys
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from meei.crypto import MEEI_DIR, encrypt, decrypt, is_initialized

CONFIG_FILE = MEEI_DIR / "config.enc"


class Config:
    """設定管理器"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def _load(self) -> Dict[str, Any]:
        """載入並解密設定"""
        if not CONFIG_FILE.exists():
            return {"providers": {}}

        encrypted = CONFIG_FILE.read_text()
        decrypted = decrypt(encrypted)
        return json.loads(decrypted)

    def _save(self, data: Dict[str, Any]):
        """加密並儲存設定"""
        json_str = json.dumps(data, indent=2)
        encrypted = encrypt(json_str)
        CONFIG_FILE.write_text(encrypted)

    def get(self, key: str, default: Any = None) -> Any:
        """
        取得設定值
        支援點號語法: config.get("deepseek.api_key")
        """
        data = self._load()
        keys = key.split(".")

        current = data.get("providers", {})
        for k in keys:
            if isinstance(current, dict):
                current = current.get(k)
            else:
                return default
            if current is None:
                return default

        return current

    def set(self, key: str, value: Any):
        """
        設定值
        支援點號語法: config.set("deepseek.api_key", "sk-xxx")
        """
        if not is_initialized():
            raise RuntimeError("meei 尚未初始化，請執行 `meei init`")

        data = self._load()
        keys = key.split(".")

        if "providers" not in data:
            data["providers"] = {}

        current = data["providers"]
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self._save(data)

    def get_provider(self, name: str) -> Dict[str, Any]:
        """取得完整的 provider 設定"""
        data = self._load()
        return data.get("providers", {}).get(name, {})

    def list_providers(self) -> list:
        """列出所有已設定的 providers"""
        data = self._load()
        return list(data.get("providers", {}).keys())

    def delete(self, key: str) -> bool:
        """刪除設定"""
        data = self._load()
        keys = key.split(".")

        current = data.get("providers", {})
        for k in keys[:-1]:
            if k not in current:
                return False
            current = current[k]

        if keys[-1] in current:
            del current[keys[-1]]
            self._save(data)
            return True
        return False


# 全域設定實例
config = Config()
