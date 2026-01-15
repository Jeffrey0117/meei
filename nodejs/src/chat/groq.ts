/**
 * Groq Chat Provider
 *
 * 支援模型:
 * - llama-3.3-70b-versatile: Llama 3.3 70B
 * - llama-3.1-8b-instant: Llama 3.1 8B (快速)
 * - mixtral-8x7b-32768: Mixtral 8x7B
 * - gemma2-9b-it: Gemma 2 9B
 */

import { ChatProvider, Message, ChatOptions, ParsedResponse } from './base.js';

const MODEL_ALIASES: Record<string, string> = {
  llama: 'llama-3.3-70b-versatile',
  llama70b: 'llama-3.3-70b-versatile',
  llama8b: 'llama-3.1-8b-instant',
  mixtral: 'mixtral-8x7b-32768',
  gemma: 'gemma2-9b-it',
};

const MODEL_PRICES: Record<string, { input: number; output: number }> = {
  'llama-3.3-70b-versatile': { input: 0.00059, output: 0.00079 },
  'llama-3.1-8b-instant': { input: 0.00005, output: 0.00008 },
  'mixtral-8x7b-32768': { input: 0.00024, output: 0.00024 },
  'gemma2-9b-it': { input: 0.0002, output: 0.0002 },
};

export class GroqChat extends ChatProvider {
  readonly PROVIDER_NAME = 'groq';
  readonly DEFAULT_MODEL = 'llama-3.3-70b-versatile';
  readonly BASE_URL = 'https://api.groq.com/openai/v1';
  readonly PRICE_INPUT = 0.00059;
  readonly PRICE_OUTPUT = 0.00079;

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
 * Groq 快捷函數
 */
export async function groq(prompt: string, options: ChatOptions = {}): Promise<string> {
  const provider = new GroqChat();
  return provider.chat(prompt, options);
}
