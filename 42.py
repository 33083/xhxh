import sys
sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI
from openai import APIConnectionError
import time
import json
import re
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLM:
    PLATFORMS = {
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-v4-pro",
        },
        "qwen": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-plus",
        },
        "glm": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4",
        },
        "spark": {
            "base_url": "https://spark-api-open.xf-yun.com/x2/",
            "model": "spark-x",
        } 
        
    }

    def __init__(self, platform: str, api_key: str = None):
        config = self.PLATFORMS[platform]
        # 如果没有传入api_key，从环境变量获取
        if api_key is None:
            api_key = os.getenv(f"{platform.upper()}_API_KEY")
        self.client = OpenAI(
            api_key=api_key,
            base_url=config["base_url"],
        )
        self.model = config["model"]
        self.temperature = 0.5
        self.platform = platform

    def chat(self, prompt: str, max_tokens: int = 100):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=max_tokens,
                stream=True, 
            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            return f"网络连接失败：无法连接到 {self.platform} API，请检查网络连接或稍后重试。"
        except Exception as e:
            return f"请求失败：{str(e)}"

if __name__ == "__main__":
    # 测试qwen（从环境变量获取密钥）
    llm = LLM("qwen")
    a=input("请输入: ")
    print("Qwen:", llm.chat(a))
    # 测试glm（从环境变量获取密钥）
    llm = LLM("glm")
    print("GLM:", llm.chat(a))
    # 测试spark（从环境变量获取密钥）
    llm = LLM("spark")
    print("Spark:", llm.chat(a))
   # 测试deepseek（从环境变量获取密钥）
    llm = LLM("deepseek")
    b=LLM("spark").chat(a)
    c=LLM("glm").chat(a)
    d=LLM("qwen").chat(a)
    print("DeepSeek:", llm.chat(f"直接告诉我哪个观点更好：{b},{c},{d}"))
