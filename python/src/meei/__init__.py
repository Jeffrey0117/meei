"""
meei - Personal AI SDK
Unified interface for multiple AI providers
"""

__version__ = "0.1.0"

# 自動載入 .env 文件
import os
from pathlib import Path

def _load_env():
    """載入 .env 文件"""
    # 尋找 .env 文件 (meei 專案根目錄)
    current = Path(__file__).resolve()
    for parent in [current.parent.parent.parent.parent.parent,  # meei/
                   current.parent.parent.parent.parent,          # meei/python/
                   Path.cwd()]:                                  # 當前目錄
        env_file = parent / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key and value and key not in os.environ:
                            os.environ[key] = value
            break

_load_env()

from meei.chat import chat
from meei.image import image
from meei.config import config

__all__ = ["chat", "image", "config", "__version__"]
