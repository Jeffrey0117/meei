"""
meei - Personal AI SDK
Unified interface for multiple AI providers
"""

__version__ = "0.1.0"

# 自動載入 .env 文件
import os
from pathlib import Path

def _load_env():
    """載入 .env 文件（優先級：系統環境變數 > 專案 .env > ~/.meei/.env）"""
    current = Path(__file__).resolve()

    # 搜索順序：專案目錄優先，全局 ~/.meei/ 最後
    env_locations = [
        current.parent.parent.parent.parent.parent / ".env",  # meei/
        current.parent.parent.parent.parent / ".env",          # meei/python/
        Path.cwd() / ".env",                                   # 當前目錄
        Path.home() / ".meei" / ".env",                        # 全局設定
    ]

    for env_file in env_locations:
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # 不覆蓋已存在的環境變數
                        if key and value and key not in os.environ:
                            os.environ[key] = value

_load_env()

from meei.chat import chat
from meei.image import image
from meei.config import config

__all__ = ["chat", "image", "config", "__version__"]
