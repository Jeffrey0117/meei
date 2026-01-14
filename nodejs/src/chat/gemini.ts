/**
 * Google Gemini Chat Provider
 *
 * 支援模型:
 * - gemini-1.5-pro: 最強多模態
 * - gemini-1.5-flash: 快速版
 * - gemini-2.0-flash-exp: 實驗版
 */

import { ChatProvider, Message, ChatOptions, ParsedResponse } from './base.js';
import { config } from '../config.js';
import { track } from '../tracker.js';
import { AuthenticationError } from '../exceptions.js';

const MODEL_ALIASES: Record<string, string> = {
  'pro': 'gemini-1.5-pro',
  'flash': 'gemini-1.5-flash',
  '2.0': 'gemini-2.0-flash-exp',
  '1.0': 'gemini-1.0-pro',
};

const MODEL_PRICES: Record<string, { input: number; output: number }> = {
  'gemini-1.5-pro': { input: 0.00125, output: 0.005 },
  'gemini-1.5-flash': { input: 0.000075, output: 0.0003 },
  'gemini-2.0-flash-exp': { input: 0, output: 0 },
  'gemini-1.0-pro': { input: 0.0005, output: 0.0015 },
};

export class GeminiChat extends ChatProvider {
  readonly PROVIDER_NAME = 'gemini';
  readonly DEFAULT_MODEL = 'gemini-1.5-flash';
  readonly BASE_URL = 'https://generativelanguage.googleapis.com/v1beta';
  readonly PRICE_INPUT = 0.000075;
  readonly PRICE_OUTPUT = 0.0003;

  private resolveModel(model: string): string {
    return MODEL_ALIASES[model] || model;
  }

  protected getHeaders(): Record<string, string> {
    return { 'Content-Type': 'application/json' };
  }

  protected calculateCost(inputTokens: number, outputTokens: number, model?: string): number {
    const m = model || this.DEFAULT_MODEL;
    const prices = MODEL_PRICES[m] || { input: this.PRICE_INPUT, output: this.PRICE_OUTPUT };
    return (inputTokens * prices.input + outputTokens * prices.output) / 1000;
  }

  private convertMessages(messages: Message[]): { contents: unknown[]; systemInstruction?: unknown } {
    const contents: unknown[] = [];
    let systemInstruction: unknown = undefined;

    for (const msg of messages) {
      if (msg.role === 'system') {
        systemInstruction = { parts: [{ text: msg.content }] };
      } else if (msg.role === 'user') {
        contents.push({ role: 'user', parts: [{ text: msg.content }] });
      } else if (msg.role === 'assistant') {
        contents.push({ role: 'model', parts: [{ text: msg.content }] });
      }
    }

    return { contents, systemInstruction };
  }

  protected buildPayload(
    messages: Message[],
    model: string,
    temperature?: number,
    maxTokens?: number,
  ): Record<string, unknown> {
    const { contents, systemInstruction } = this.convertMessages(messages);

    const payload: Record<string, unknown> = { contents };
    if (systemInstruction) payload.systemInstruction = systemInstruction;

    const generationConfig: Record<string, unknown> = {};
    if (temperature !== undefined) generationConfig.temperature = temperature;
    if (maxTokens !== undefined) generationConfig.maxOutputTokens = maxTokens;
    if (Object.keys(generationConfig).length) payload.generationConfig = generationConfig;

    return payload;
  }

  protected parseResponse(data: Record<string, unknown>): ParsedResponse {
    const candidates = data.candidates as Array<{ content: { parts: Array<{ text: string }> } }>;
    const parts = candidates?.[0]?.content?.parts || [];
    const content = parts.map(p => p.text).join('');

    const usage = data.usageMetadata as { promptTokenCount: number; candidatesTokenCount: number } | undefined;
    const inputTokens = usage?.promptTokenCount || 0;
    const outputTokens = usage?.candidatesTokenCount || 0;
    const model = (data.modelVersion as string) || this.DEFAULT_MODEL;

    return { content, inputTokens, outputTokens, model };
  }

  async conversation(messages: Message[], options: ChatOptions = {}): Promise<string> {
    const model = this.resolveModel(options.model || this.DEFAULT_MODEL);

    if (options.system && (!messages.length || messages[0].role !== 'system')) {
      messages = [{ role: 'system', content: options.system }, ...messages];
    }

    const payload = this.buildPayload(messages, model, options.temperature, options.maxTokens);
    const endpoint = `${this.baseUrl}/models/${model}:generateContent?key=${this.apiKey}`;

    const startTime = Date.now();

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(payload),
    });

    const latencyMs = Date.now() - startTime;

    if (!response.ok) {
      const body = await response.text();
      this.handleError(response.status, body);
    }

    const data = await response.json() as Record<string, unknown>;
    const { content, inputTokens, outputTokens } = this.parseResponse(data);

    track({
      provider: this.PROVIDER_NAME,
      type: 'chat',
      model,
      input_tokens: inputTokens,
      output_tokens: outputTokens,
      cost: this.calculateCost(inputTokens, outputTokens, model),
      latency_ms: latencyMs,
      prompt: messages[messages.length - 1]?.content,
    });

    return content;
  }
}

/**
 * Gemini 快捷函數
 */
export async function gemini(prompt: string, options: ChatOptions = {}): Promise<string> {
  const provider = new GeminiChat();
  return provider.chat(prompt, options);
}
