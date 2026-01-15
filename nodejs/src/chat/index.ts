/**
 * Chat 模組 - 統一聊天介面
 */

import { ChatProvider, Message, ChatOptions } from './base.js';
import { DeepSeekChat, deepseek } from './deepseek.js';
import { OpenAIChat, openai } from './openai.js';
import { GeminiChat, gemini } from './gemini.js';
import { QwenChat, qwen } from './qwen.js';
import { GrokChat, grok } from './grok.js';
import { GroqChat, groq } from './groq.js';

// Provider 映射
const PROVIDERS: Record<string, new () => ChatProvider> = {
  deepseek: DeepSeekChat,
  openai: OpenAIChat,
  chatgpt: OpenAIChat,
  gemini: GeminiChat,
  qwen: QwenChat,
  grok: GrokChat,
  groq: GroqChat,
};

const DEFAULT_PROVIDER = 'deepseek';

class Chat {
  private instances: Map<string, ChatProvider> = new Map();

  private getProvider(pv: string): ChatProvider {
    if (!this.instances.has(pv)) {
      const ProviderClass = PROVIDERS[pv];
      if (!ProviderClass) {
        const available = Object.keys(PROVIDERS).join(', ');
        throw new Error(`不支援的 provider: ${pv}，可用: ${available}`);
      }
      this.instances.set(pv, new ProviderClass());
    }
    return this.instances.get(pv)!;
  }

  /**
   * 發送聊天請求
   */
  async ask(
    prompt: string,
    options: ChatOptions & { pv?: string } = {}
  ): Promise<string> {
    const pv = options.pv || DEFAULT_PROVIDER;
    const provider = this.getProvider(pv);
    return provider.chat(prompt, options);
  }

  /**
   * 多輪對話
   */
  async conversation(
    messages: Message[],
    options: ChatOptions & { pv?: string } = {}
  ): Promise<string> {
    const pv = options.pv || DEFAULT_PROVIDER;
    const provider = this.getProvider(pv);
    return provider.conversation(messages, options);
  }
}

// 全域實例
export const chat = new Chat();

// 匯出所有
export { ChatProvider, Message, ChatOptions } from './base.js';
export { DeepSeekChat, deepseek } from './deepseek.js';
export { OpenAIChat, openai } from './openai.js';
export { GeminiChat, gemini } from './gemini.js';
export { QwenChat, qwen } from './qwen.js';
export { GrokChat, grok } from './grok.js';
export { GroqChat, groq } from './groq.js';
