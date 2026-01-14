# meei

統一 AI Chat 介面 - 一套 API 打所有 LLM

## 支援 Provider

| Provider | 模型 | 別名 |
|----------|------|------|
| DeepSeek | deepseek-chat, deepseek-coder, deepseek-reasoner | chat, coder, r1 |
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo | 4o, 4o-mini, turbo |
| Gemini | gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp | pro, flash, 2.0 |
| Qwen | qwen-turbo, qwen-plus, qwen-max, qwen-long | turbo, plus, max, long |
| Grok | grok-2, grok-2-mini | 2, mini |

## 安裝

### Python

```bash
cd python
pip install -e .
```

### Node.js

```bash
cd nodejs
npm install
npm run build
```

## 設定 API Key

```bash
# Python
meei config set deepseek.api_key sk-xxx
meei config set openai.api_key sk-xxx

# 或直接編輯 ~/.meei/config.json
```

## 使用方式

### Python

```python
from meei.chat import chat

# 統一介面 - 切換 provider 只改 pv 參數
response = chat.ask("你好", pv="deepseek")
response = chat.ask("Hello", pv="openai", model="4o")
response = chat.ask("寫程式", pv="gemini", model="pro")

# 快捷函數
from meei.chat.deepseek import deepseek
from meei.chat.openai import openai

response = deepseek("寫個快速排序", model="coder")
response = openai("解釋量子力學", model="4o")

# 多輪對話
messages = [
    {"role": "user", "content": "我叫小明"},
    {"role": "assistant", "content": "你好小明！"},
    {"role": "user", "content": "我叫什麼？"},
]
response = chat.conversation(messages, pv="deepseek")

# 串流輸出
for chunk in chat.ask("講個故事", pv="deepseek", stream=True):
    print(chunk, end="")

# System prompt
response = chat.ask(
    "寫個網頁",
    pv="deepseek",
    model="coder",
    system="你是資深前端工程師，用 React + TypeScript",
    temperature=0.7,
    max_tokens=2000,
)
```

### Node.js / TypeScript

```typescript
import { chat, deepseek, openai } from 'meei';

// 統一介面
const response = await chat.ask("你好", { pv: "deepseek" });
const response = await chat.ask("Hello", { pv: "openai", model: "4o" });

// 快捷函數
const response = await deepseek("寫個快速排序", { model: "coder" });
const response = await openai("解釋量子力學", { model: "4o" });

// 多輪對話
const messages = [
    { role: "user", content: "我叫小明" },
    { role: "assistant", content: "你好小明！" },
    { role: "user", content: "我叫什麼？" },
];
const response = await chat.conversation(messages, { pv: "deepseek" });

// 帶選項
const response = await chat.ask("寫個網頁", {
    pv: "deepseek",
    model: "coder",
    system: "你是資深前端工程師",
    temperature: 0.7,
    maxTokens: 2000,
});
```

## 用量追蹤

所有請求自動記錄到 `~/.meei/usage.json`，包含：
- Provider / Model
- Input / Output tokens
- 花費 (USD)
- 延遲 (ms)

開啟 `dashboard/index.html` 查看視覺化統計。

## 專案結構

```
meei/
├── python/           # Python SDK
│   └── src/meei/
│       ├── chat/     # Chat providers
│       ├── config.py # 設定管理
│       └── tracker.py # 用量追蹤
├── nodejs/           # Node.js SDK (TypeScript)
│   └── src/
│       ├── chat/     # Chat providers
│       ├── config.ts
│       └── tracker.ts
└── dashboard/        # 用量儀表板
    ├── index.html
    └── app.js
```

## License

MIT
