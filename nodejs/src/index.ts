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

import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

// 自動載入 .env（優先級：系統環境變數 > 專案 .env > ~/.meei/.env）
function loadEnv(): void {
  const envLocations = [
    join(process.cwd(), '.env'),           // 專案目錄
    join(homedir(), '.meei', '.env'),      // 全局設定
  ];

  for (const envPath of envLocations) {
    if (existsSync(envPath)) {
      try {
        const content = readFileSync(envPath, 'utf-8');
        for (const line of content.split('\n')) {
          const trimmed = line.trim();
          if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
            const [key, ...valueParts] = trimmed.split('=');
            const value = valueParts.join('=');
            // 不覆蓋已存在的環境變數
            if (key && value && !(key in process.env)) {
              process.env[key] = value;
            }
          }
        }
      } catch {
        // 忽略讀取錯誤
      }
    }
  }
}

loadEnv();

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
