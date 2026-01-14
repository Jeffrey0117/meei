/**
 * 用量追蹤模組
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const MEEI_DIR = join(homedir(), '.meei');
const USAGE_FILE = join(MEEI_DIR, 'usage.json');

interface UsageRecord {
  timestamp: string;
  provider: string;
  type: string;
  model: string;
  input_tokens?: number;
  output_tokens?: number;
  cost?: number;
  latency_ms?: number;
  prompt?: string;
}

interface UsageData {
  records: UsageRecord[];
  total_cost: number;
}

function loadUsage(): UsageData {
  if (!existsSync(USAGE_FILE)) {
    return { records: [], total_cost: 0 };
  }
  const content = readFileSync(USAGE_FILE, 'utf-8');
  return JSON.parse(content);
}

function saveUsage(data: UsageData): void {
  if (!existsSync(MEEI_DIR)) {
    mkdirSync(MEEI_DIR, { recursive: true });
  }
  writeFileSync(USAGE_FILE, JSON.stringify(data, null, 2));
}

/**
 * 記錄用量
 */
export function track(params: {
  provider: string;
  type: string;
  model: string;
  input_tokens?: number;
  output_tokens?: number;
  cost?: number;
  latency_ms?: number;
  prompt?: string;
}): void {
  const data = loadUsage();

  const record: UsageRecord = {
    timestamp: new Date().toISOString(),
    provider: params.provider,
    type: params.type,
    model: params.model,
    input_tokens: params.input_tokens,
    output_tokens: params.output_tokens,
    cost: params.cost,
    latency_ms: params.latency_ms,
    prompt: params.prompt?.substring(0, 100), // 只存前 100 字
  };

  data.records.push(record);
  if (params.cost) {
    data.total_cost += params.cost;
  }

  saveUsage(data);
}

/**
 * 取得用量統計
 */
export function getUsage(): UsageData {
  return loadUsage();
}

/**
 * 清除用量記錄
 */
export function clearUsage(): void {
  saveUsage({ records: [], total_cost: 0 });
}
