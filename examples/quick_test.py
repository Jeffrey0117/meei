"""
meei 快速測試 - 單一 Provider 測試

用法:
    python quick_test.py deepseek "你好"
    python quick_test.py openai "Hello" gpt-4o
    python quick_test.py gemini "寫程式" pro
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python", "src"))

from meei.chat import chat


def main():
    if len(sys.argv) < 3:
        print("用法: python quick_test.py <provider> <prompt> [model]")
        print()
        print("範例:")
        print('  python quick_test.py deepseek "你好"')
        print('  python quick_test.py openai "Hello" 4o')
        print('  python quick_test.py gemini "寫程式" pro')
        sys.exit(1)

    pv = sys.argv[1]
    prompt = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Provider: {pv}")
    print(f"Model: {model or '(default)'}")
    print(f"Prompt: {prompt}")
    print("-" * 40)

    try:
        response = chat.ask(prompt, pv=pv, model=model)
        print(response)
    except Exception as e:
        print(f"錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
