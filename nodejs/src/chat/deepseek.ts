/**
 * DeepSeek Chat Provider
 *
 * 支援模型:
 * - deepseek-chat: 通用對話模型
 * - deepseek-coder: 程式碼專用模型
 * - deepseek-reasoner: 推理模型 (R1)
 */

import { ChatProvider, Message, ChatOptions, ParsedResponse } from './base.js';

const MODEL_ALIASES: Record<string, string> = {
  'chat': 'deepseek-chat',
  'coder': 'deepseek-coder',
  'reasoner': 'deepseek-reasoner',
  'r1': 'deepseek-reasoner',
};

const MODEL_PRICES: Record<string, { input: number; output: number }> = {
  'deepseek-chat': { input: 0.00014, output: 0.00028 },
  'deepseek-coder': { input: 0.00014, output: 0.00028 },
  'deepseek-reasoner': { input: 0.00055, output: 0.00219 },
};

export class DeepSeekChat extends ChatProvider {
  readonly PROVIDER_NAME = 'deepseek';
  readonly DEFAULT_MODEL = 'deepseek-chat';
  readonly BASE_URL = 'https://api.deepseek.com';
  readonly PRICE_INPUT = 0.00014;
  readonly PRICE_OUTPUT = 0.00028;

  private resolveModel(model: string): string {
    return MODEL_ALIASES[model] || model;
  }

  protected calculateCost(inputTokens: number, outputTokens: number, model?: string): number {
    const m = model || this.DEFAULT_MODEL;
    const prices = MODEL_PRICES[m] || { input: this.PRICE_INPUT, output: this.PRICE_OUTPUT };
    return (inputTokens * prices.input + outputTokens * prices.output) / 1000;
  }

  protected buildPayload(
    messages: Message[],
    model: string,
    temperature?: number,
    maxTokens?: number,
    stream?: boolean
  ): Record<string, unknown> {
    const payload: Record<string, unknown> = {
      model: this.resolveModel(model),
      messages,
      stream: stream || false,
    };

    if (temperature !== undefined) payload.temperature = temperature;
    if (maxTokens !== undefined) payload.max_tokens = maxTokens;

    return payload;
  }

  protected parseResponse(data: Record<string, unknown>): ParsedResponse {
    const choices = data.choices as Array<{ message: { content: string } }>;
    const content = choices?.[0]?.message?.content || '';

    const usage = data.usage as { prompt_tokens: number; completion_tokens: number } | undefined;
    const inputTokens = usage?.prompt_tokens || 0;
    const outputTokens = usage?.completion_tokens || 0;
    const model = (data.model as string) || this.DEFAULT_MODEL;

    return { content, inputTokens, outputTokens, model };
  }
}

/**
 * DeepSeek 快捷函數
 */
export async function deepseek(prompt: string, options: ChatOptions = {}): Promise<string> {
  const provider = new DeepSeekChat();
  return provider.chat(prompt, options);
}
