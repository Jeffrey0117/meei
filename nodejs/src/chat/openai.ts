/**
 * OpenAI Chat Provider
 *
 * 支援模型:
 * - gpt-4o: 最新多模態模型
 * - gpt-4o-mini: 輕量版
 * - gpt-4-turbo: GPT-4 Turbo
 * - gpt-3.5-turbo: GPT-3.5
 */

import { ChatProvider, Message, ChatOptions, ParsedResponse } from './base.js';

const MODEL_ALIASES: Record<string, string> = {
  '4o': 'gpt-4o',
  '4o-mini': 'gpt-4o-mini',
  '4-turbo': 'gpt-4-turbo',
  '3.5': 'gpt-3.5-turbo',
  'turbo': 'gpt-3.5-turbo',
};

const MODEL_PRICES: Record<string, { input: number; output: number }> = {
  'gpt-4o': { input: 0.0025, output: 0.01 },
  'gpt-4o-mini': { input: 0.00015, output: 0.0006 },
  'gpt-4-turbo': { input: 0.01, output: 0.03 },
  'gpt-3.5-turbo': { input: 0.0005, output: 0.0015 },
};

export class OpenAIChat extends ChatProvider {
  readonly PROVIDER_NAME = 'openai';
  readonly DEFAULT_MODEL = 'gpt-4o-mini';
  readonly BASE_URL = 'https://api.openai.com/v1';
  readonly PRICE_INPUT = 0.00015;
  readonly PRICE_OUTPUT = 0.0006;

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
 * OpenAI 快捷函數
 */
export async function openai(prompt: string, options: ChatOptions = {}): Promise<string> {
  const provider = new OpenAIChat();
  return provider.chat(prompt, options);
}
