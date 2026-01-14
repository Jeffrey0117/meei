/**
 * 自定義例外
 */

export class MeeiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'MeeiError';
  }
}

export class ConfigError extends MeeiError {
  constructor(message: string) {
    super(message);
    this.name = 'ConfigError';
  }
}

export class ProviderError extends MeeiError {
  provider: string;

  constructor(provider: string, message: string) {
    super(`[${provider}] ${message}`);
    this.name = 'ProviderError';
    this.provider = provider;
  }
}

export class AuthenticationError extends ProviderError {
  constructor(provider: string, message: string) {
    super(provider, message);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends ProviderError {
  constructor(provider: string, message: string) {
    super(provider, message);
    this.name = 'RateLimitError';
  }
}

export class APIError extends ProviderError {
  statusCode: number;

  constructor(provider: string, statusCode: number, message: string) {
    super(provider, `HTTP ${statusCode}: ${message}`);
    this.name = 'APIError';
    this.statusCode = statusCode;
  }
}
