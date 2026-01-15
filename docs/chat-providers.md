# Chat Providers 測試紀錄

測試日期: 2026-01-15

## 測試結果

| Provider | BASE_URL | 預設模型 | 狀態 |
|----------|----------|----------|------|
| deepseek | `https://api.deepseek.com` | deepseek-chat | ✓ OK |
| openai | `https://api.openai.com/v1` | gpt-4o-mini | ✓ OK |
| gemini | `https://generativelanguage.googleapis.com/v1beta` | gemini-2.0-flash | ✓ OK |
| qwen | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | qwen-turbo | ✓ OK |
| groq | `https://api.groq.com/openai/v1` | llama-3.3-70b-versatile | ✓ OK |

## API 格式

### OpenAI 兼容格式 (deepseek, openai, qwen, groq)

```
POST {base_url}/chat/completions
Headers:
  Authorization: Bearer {api_key}
  Content-Type: application/json

Body:
{
  "model": "model-name",
  "messages": [{"role": "user", "content": "..."}],
  "temperature": 0.7,
  "max_tokens": 2000,
  "stream": false
}
```

### Gemini 格式

```
POST {base_url}/models/{model}:generateContent?key={api_key}
Headers:
  Content-Type: application/json

Body:
{
  "contents": [{"role": "user", "parts": [{"text": "..."}]}],
  "systemInstruction": {"parts": [{"text": "..."}]},
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 2000
  }
}
```

## 環境變數

```bash
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
GEMINI_API_KEY=AIza-xxx
QWEN_API_KEY=sk-xxx
GROQ_API_KEY=gsk_xxx
```
