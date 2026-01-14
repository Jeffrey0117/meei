"""
自定義例外
"""


class MeeiError(Exception):
    """meei 基礎例外"""

    pass


class ConfigError(MeeiError):
    """設定錯誤"""

    pass


class ProviderError(MeeiError):
    """Provider 錯誤"""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class AuthenticationError(ProviderError):
    """認證錯誤 - API key 無效"""

    pass


class RateLimitError(ProviderError):
    """超過請求限制"""

    pass


class APIError(ProviderError):
    """API 回應錯誤"""

    def __init__(self, provider: str, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(provider, f"HTTP {status_code}: {message}")
