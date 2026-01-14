/**
 * xAI Grok Chat Provider
 *
 * 支援模型:
 * - grok-2: 最新版
 * - grok-2-mini: 輕量版
 * - grok-beta: Beta 版
 */

import { ChatProvider, Message, ChatOptions, ParsedResponse } from './base.js';

const MODEL_ALIASES: Record<string, string> = {
  '2': 'grok-2',
  'mini': 'grok-2-mini',
  'beta': 'grok-beta',
};

const MODEL_PRICES: Record<string, { input: number; output: number }> = {
  'grok-2': { input: 0.002, output: 0.01 },
  'grok-2-mini': { input: 0.0002, output: 0.001 },
  'grok-beta': { input: 0.002, output: 0.01 },
};

export class GrokChat extends ChatProvider {
  readonly PROVIDER_NAME = 'grok';
  readonly DEFAULT_MODEL = 'grok-2';
  readonly BASE_URL = 'https://api.x.ai/v1';
  readonly PRICE_INPUT = 0.002;
  readonly PRICE_OUTPUT = 0.01;

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
 * Grok 快捷函數
 */
export async function grok(prompt: string, options: ChatOptions = {}): Promise<string> {
  const provider = new GrokChat();
  return provider.chat(prompt, options);
}
