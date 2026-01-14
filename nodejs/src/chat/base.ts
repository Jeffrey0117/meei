/**
 * Chat Provider 基礎類別
 */

import { config } from '../config.js';
import { track } from '../tracker.js';
import { AuthenticationError, RateLimitError, APIError } from '../exceptions.js';

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatOptions {
  model?: string;
  system?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
}

export interface ParsedResponse {
  content: string;
  inputTokens: number;
  outputTokens: number;
  model: string;
}

export abstract class ChatProvider {
  abstract readonly PROVIDER_NAME: string;
  abstract readonly DEFAULT_MODEL: string;
  abstract readonly BASE_URL: string;
  abstract readonly PRICE_INPUT: number;
  abstract readonly PRICE_OUTPUT: number;

  get apiKey(): string {
    const key = config.get(`${this.PROVIDER_NAME}.api_key`) as string;
    if (!key) {
      throw new AuthenticationError(
        this.PROVIDER_NAME,
        `未設定 API key，請執行: meei config set ${this.PROVIDER_NAME}.api_key YOUR_KEY`
      );
    }
    return key;
  }

  get baseUrl(): string {
    return (config.get(`${this.PROVIDER_NAME}.base_url`) as string) || this.BASE_URL;
  }

  protected getHeaders(): Record<string, string> {
    return {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  protected calculateCost(inputTokens: number, outputTokens: number): number {
    return (inputTokens * this.PRICE_INPUT + outputTokens * this.PRICE_OUTPUT) / 1000;
  }

  protected handleError(statusCode: number, body: string): never {
    if (statusCode === 401) {
      throw new AuthenticationError(this.PROVIDER_NAME, 'API key 無效');
    } else if (statusCode === 429) {
      throw new RateLimitError(this.PROVIDER_NAME, '超過請求限制，請稍後再試');
    } else {
      let errorMsg = body;
      try {
        const parsed = JSON.parse(body);
        errorMsg = parsed.error?.message || body;
      } catch {}
      throw new APIError(this.PROVIDER_NAME, statusCode, errorMsg);
    }
  }

  protected abstract buildPayload(
    messages: Message[],
    model: string,
    temperature?: number,
    maxTokens?: number,
    stream?: boolean
  ): Record<string, unknown>;

  protected abstract parseResponse(data: Record<string, unknown>): ParsedResponse;

  /**
   * 發送聊天請求
   */
  async chat(prompt: string, options: ChatOptions = {}): Promise<string> {
    const messages: Message[] = [];
    if (options.system) {
      messages.push({ role: 'system', content: options.system });
    }
    messages.push({ role: 'user', content: prompt });

    return this.conversation(messages, options);
  }

  /**
   * 多輪對話
   */
  async conversation(messages: Message[], options: ChatOptions = {}): Promise<string> {
    const model = options.model || this.DEFAULT_MODEL;

    if (options.system && (!messages.length || messages[0].role !== 'system')) {
      messages = [{ role: 'system', content: options.system }, ...messages];
    }

    const payload = this.buildPayload(
      messages,
      model,
      options.temperature,
      options.maxTokens,
      options.stream
    );

    const startTime = Date.now();

    const response = await fetch(`${this.baseUrl}/chat/completions`, {
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
    const { content, inputTokens, outputTokens, model: usedModel } = this.parseResponse(data);

    track({
      provider: this.PROVIDER_NAME,
      type: 'chat',
      model: usedModel,
      input_tokens: inputTokens,
      output_tokens: outputTokens,
      cost: this.calculateCost(inputTokens, outputTokens),
      latency_ms: latencyMs,
      prompt: messages[messages.length - 1]?.content,
    });

    return content;
  }
}
