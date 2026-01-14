"""
meei - Personal AI SDK
Unified interface for multiple AI providers
"""

__version__ = "0.1.0"

from meei.chat import chat
from meei.image import image
from meei.config import config

__all__ = ["chat", "image", "config", "__version__"]
