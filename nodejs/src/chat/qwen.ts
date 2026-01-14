/**
 * Alibaba Qwen (通義千問) Chat Provider
 *
 * 支援模型:
 * - qwen-turbo: 快速版
 * - qwen-plus: 增強版
 * - qwen-max: 最強版
 * - qwen-long: 長文本版
 * - qwen-coder-turbo: 程式碼專用
 */

import { ChatProvider, Message, ChatOptions, ParsedResponse } from './base.js';

const MODEL_ALIASES: Record<string, string> = {
  'turbo': 'qwen-turbo',
  'plus': 'qwen-plus',
  'max': 'qwen-max',
  'long': 'qwen-long',
  'coder': 'qwen-coder-turbo',
};

const MODEL_PRICES: Record<string, { input: number; output: number }> = {
  'qwen-turbo': { input: 0.000042, output: 0.000083 },
  'qwen-plus': { input: 0.00011, output: 0.00028 },
  'qwen-max': { input: 0.0028, output: 0.0083 },
  'qwen-long': { input: 0.00007, output: 0.00028 },
  'qwen-coder-turbo': { input: 0.00028, output: 0.00083 },
};

export class QwenChat extends ChatProvider {
  readonly PROVIDER_NAME = 'qwen';
  readonly DEFAULT_MODEL = 'qwen-turbo';
  readonly BASE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1';
  readonly PRICE_INPUT = 0.000042;
  readonly PRICE_OUTPUT = 0.000083;

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
 * Qwen 快捷函數
 */
export async function qwen(prompt: string, options: ChatOptions = {}): Promise<string> {
  const provider = new QwenChat();
  return provider.chat(prompt, options);
}
