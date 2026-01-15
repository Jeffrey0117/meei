/**
 * meei - 統一 AI Chat 介面
 *
 * 支援 Provider:
 * - DeepSeek (deepseek-chat, deepseek-coder, deepseek-reasoner)
 * - OpenAI (gpt-4o, gpt-4o-mini, gpt-4-turbo)
 * - Google Gemini (gemini-1.5-pro, gemini-1.5-flash)
 * - Alibaba Qwen (qwen-turbo, qwen-plus, qwen-max)
 * - xAI Grok (grok-2, grok-2-mini)
 * - Groq (llama-3.3-70b-versatile, mixtral-8x7b)
 *
 * @example
 * ```typescript
 * import { chat, deepseek, openai } from 'meei';
 *
 * // 統一介面
 * const response = await chat.ask('你好', { pv: 'deepseek' });
 *
 * // 快捷函數
 * const response = await deepseek('寫個快排', { model: 'coder' });
 * ```
 */

// Chat 模組
export { chat, deepseek, openai, gemini, qwen, grok, groq } from './chat/index.js';
export type { Message, ChatOptions } from './chat/base.js';

// Config
export { config } from './config.js';

// Tracker
export { track, getUsage, clearUsage } from './tracker.js';

// Exceptions
export {
  MeeiError,
  ConfigError,
  ProviderError,
  AuthenticationError,
  RateLimitError,
  APIError,
} from './exceptions.js';
