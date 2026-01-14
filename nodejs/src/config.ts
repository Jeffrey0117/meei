/**
 * 設定管理模組
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const MEEI_DIR = join(homedir(), '.meei');
const CONFIG_FILE = join(MEEI_DIR, 'config.json');

interface ProviderConfig {
  api_key?: string;
  base_url?: string;
  [key: string]: unknown;
}

interface ConfigData {
  providers: Record<string, ProviderConfig>;
}

class Config {
  private load(): ConfigData {
    if (!existsSync(CONFIG_FILE)) {
      return { providers: {} };
    }
    const content = readFileSync(CONFIG_FILE, 'utf-8');
    return JSON.parse(content);
  }

  private save(data: ConfigData): void {
    if (!existsSync(MEEI_DIR)) {
      mkdirSync(MEEI_DIR, { recursive: true });
    }
    writeFileSync(CONFIG_FILE, JSON.stringify(data, null, 2));
  }

  /**
   * 取得設定值
   * 支援點號語法: config.get("deepseek.api_key")
   */
  get(key: string, defaultValue: unknown = null): unknown {
    const data = this.load();
    const keys = key.split('.');

    let current: unknown = data.providers;
    for (const k of keys) {
      if (current && typeof current === 'object' && k in current) {
        current = (current as Record<string, unknown>)[k];
      } else {
        return defaultValue;
      }
    }
    return current ?? defaultValue;
  }

  /**
   * 設定值
   * 支援點號語法: config.set("deepseek.api_key", "sk-xxx")
   */
  set(key: string, value: unknown): void {
    const data = this.load();
    const keys = key.split('.');

    if (!data.providers) {
      data.providers = {};
    }

    let current: Record<string, unknown> = data.providers;
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!(k in current)) {
        current[k] = {};
      }
      current = current[k] as Record<string, unknown>;
    }
    current[keys[keys.length - 1]] = value;

    this.save(data);
  }

  /**
   * 取得完整的 provider 設定
   */
  getProvider(name: string): ProviderConfig {
    const data = this.load();
    return data.providers[name] || {};
  }

  /**
   * 列出所有已設定的 providers
   */
  listProviders(): string[] {
    const data = this.load();
    return Object.keys(data.providers);
  }

  /**
   * 刪除設定
   */
  delete(key: string): boolean {
    const data = this.load();
    const keys = key.split('.');

    let current: Record<string, unknown> = data.providers;
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!(k in current)) {
        return false;
      }
      current = current[k] as Record<string, unknown>;
    }

    const lastKey = keys[keys.length - 1];
    if (lastKey in current) {
      delete current[lastKey];
      this.save(data);
      return true;
    }
    return false;
  }
}

export const config = new Config();
