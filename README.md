# meei

**Unified AI SDK for Developers** - 統一多家 LLM 的程式介面

> 這是開發用的 SDK，讓你在程式碼中用同一套 API 呼叫 DeepSeek、OpenAI、Gemini、Qwen、Grok 等 LLM。
> 支援 Python 和 Node.js/TypeScript。

## 為什麼用 meei？

- **統一介面**: 換 provider 只改一個參數，不用重寫程式
- **模型別名**: 用 `4o` 取代 `gpt-4o`，用 `r1` 取代 `deepseek-reasoner`
- **用量追蹤**: 自動記錄 token 用量和花費
- **串流支援**: 內建串流輸出

## 支援的 Provider

| Provider | 模型 | 別名 |
|----------|------|------|
| DeepSeek | deepseek-chat, deepseek-coder, deepseek-reasoner | chat, coder, r1 |
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo | 4o, 4o-mini, turbo |
| Gemini | gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp | pro, flash, 2.0 |
| Qwen | qwen-turbo, qwen-plus, qwen-max, qwen-long | turbo, plus, max, long |
| Grok | grok-2, grok-2-mini | 2, mini |

## 安裝

```bash
# Python
cd python && pip install -e .

# Node.js
cd nodejs && npm install && npm run build
```

## 設定 API Key

```bash
meei config set deepseek.api_key sk-xxx
meei config set openai.api_key sk-xxx
# 或直接編輯 ~/.meei/config.json
```

## Quick Start

### Python

```python
from meei.chat import chat

# 切 provider 只改 pv 參數
response = chat.ask("你好", pv="deepseek")
response = chat.ask("Hello", pv="openai", model="4o")

# 快捷函數
from meei.chat.deepseek import deepseek
response = deepseek("寫個快速排序", model="coder")

# 串流
for chunk in chat.ask("講個故事", pv="deepseek", stream=True):
    print(chunk, end="")

# 多輪對話
messages = [
    {"role": "user", "content": "我叫小明"},
    {"role": "assistant", "content": "你好小明！"},
    {"role": "user", "content": "我叫什麼？"},
]
response = chat.conversation(messages, pv="deepseek")
```

### Node.js / TypeScript

```typescript
import { chat, deepseek } from 'meei';

const response = await chat.ask("你好", { pv: "deepseek" });
const response = await deepseek("寫程式", { model: "coder" });

// 多輪對話
const messages = [
    { role: "user", content: "我叫小明" },
    { role: "assistant", content: "你好小明！" },
    { role: "user", content: "我叫什麼？" },
];
const response = await chat.conversation(messages, { pv: "deepseek" });
```

## 用量追蹤

所有請求自動記錄到 `~/.meei/usage.json`（token 數、花費、延遲）。
開 `dashboard/index.html` 可看視覺化統計。

## 專案結構

```
meei/
├── python/     # Python SDK
├── nodejs/     # Node.js SDK (TypeScript)
└── dashboard/  # 用量儀表板
```

## License

MIT
