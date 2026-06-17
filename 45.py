import requests
import re
import os
from openai import OpenAI
from openai import APIConnectionError
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from docx import Document
import jieba
import jieba.analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from typing import Optional

load_dotenv()


class LLM:
    PLATFORMS = {
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",          # 修正为有效模型名，您可改为 deepseek-v4-pro 或 deepseek-chat
        }
    }

    def __init__(self, platform: str, api_key: str = None):
        config = self.PLATFORMS[platform]
        if api_key is None:
            api_key = os.getenv(f"{platform.upper()}_API_KEY")
        self.client = OpenAI(
            api_key=api_key,
            base_url=config["base_url"],
        )
        self.model = config["model"]
        self.temperature = 0.7
        self.platform = platform

    def chat_stream(self, messages: list, max_tokens: int = 300):
        """流式生成器，逐块返回内容"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                stream=True,
            )
        except APIConnectionError as e:
            yield f"网络连接失败：{str(e)}"
            return
        except Exception as e:
            yield f"请求失败：{str(e)}"
            return

        for chunk in response:
            delta = chunk.choices[0].delta
            content = delta.content if delta and delta.content else ""
            if content:
                yield content
    
    def chat(self, prompt: str, max_tokens: int = 800):
        """简单的聊天接口，支持设置最大输出长度"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            return f"网络连接失败：无法连接到 {self.platform} API"
        except Exception as e:
            return f"请求失败：{str(e)}"


# ------------------- 读取不同来源 -------------------
def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_webpage_text(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup.get_text(separator='\n', strip=True)

def read_docx(file_path):
    doc = Document(file_path)
    return '\n'.join(para.text for para in doc.paragraphs)

def read_input(source: str, input_type: str = "auto") -> str:
    """自动判断输入类型并读取"""
    if input_type == "auto":
        if source.startswith(('http://', 'https://')):
            input_type = "url"
        elif os.path.isfile(source):
            ext = os.path.splitext(source)[1].lower()
            input_type = "docx" if ext == ".docx" else "txt"
        else:
            input_type = "text"

    if input_type == "url":
        return read_webpage_text(source)
    elif input_type == "txt":
        return read_txt(source)
    elif input_type == "docx":
        return read_docx(source)
    else:
        return source   # 直接粘贴的文本


# ------------------- 文本预处理 -------------------
def clean_text(raw_text: str) -> str:
    """清洗：去掉HTML残留、多余换行和空格"""
    # 移除可能的HTML标签
    text = re.sub(r'<[^>]+>', '', raw_text)
    # 多个换行合并为两个
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # 合并连续空格
    text = re.sub(r' +', ' ', text)
    # 去掉每行首尾空白
    lines = [line.strip() for line in text.splitlines()]
    text = '\n'.join(line for line in lines if line)
    return text


# ------------------- 关键词与词云 -------------------
def extract_keywords(text: str, topk: int = 10) -> list:
    """用 jieba TF-IDF 提取关键词"""
    return jieba.analyse.extract_tags(text, topK=topk)

def generate_wordcloud(keywords: list, output_image: str = "wordcloud.png") -> str:
    """生成词云图片，返回文件名"""
    if not keywords:
        return ""
    # 词频字典（简单版：每个关键词权重为1）
    freq = {kw: 1 for kw in keywords}
    # 中文字体路径（请根据您的系统修改）
    font_path = "C:/Windows/Fonts/simhei.ttf"   # Windows
    # Mac 常用字体： "/System/Library/Fonts/PingFang.ttc"
    # Linux 可以复制一个中文字体到当前目录，或使用默认（可能乱码）
    if not os.path.exists(font_path):
        font_path = None   # 无中文字体时可能显示方框
    wc = WordCloud(
        width=800, height=400,
        background_color='white',
        font_path=font_path
    )
    wc.generate_from_frequencies(freq)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(output_image, dpi=150, bbox_inches='tight')
    plt.close()
    return output_image


# ------------------- 调用 LLM 生成三种摘要 -------------------
def generate_summaries(text: str, llm: LLM) -> dict:
    """返回三种摘要文本"""
    # 避免超过上下文限制（deepseek 一般支持 8K，取前 4000 字符足够）
    truncated = text[:4000] if len(text) > 4000 else text

    # 简短版
    short_prompt = f"请用一句话概括以下文章的核心观点（不超过30字）：\n{truncated}"
    short_summary = llm.chat(short_prompt, max_tokens=60)

    # 标准版
    medium_prompt = f"请用3到5句话概括以下文章，保留关键论据和结论：\n{truncated}"
    medium_summary = llm.chat(medium_prompt, max_tokens=300)

    # 详细版（Q&A）
    long_prompt = f"请阅读以下文章，然后提炼出3个最核心的问题及其答案，以 Q&A 格式输出（每个问题单独一行，答案另起一行）：\n{truncated}"
    long_summary = llm.chat(long_prompt, max_tokens=600)

    return {
        "short": short_summary,
        "medium": medium_summary,
        "long": long_summary
    }


# ------------------- 主程序 -------------------
def main():
    print("=== 文章摘要生成器（支持 TXT / DOCX / URL / 直接文本）===")
    source = input("请输入文件路径 / URL / 直接粘贴文本：").strip()
    if not source:
        print("输入不能为空")
        return

    # 可选：手动指定类型（不指定则自动判断）
    type_hint = input("输入类型（auto/txt/docx/url/text，回车默认 auto）：").strip()
    if type_hint not in ["auto", "txt", "docx", "url", "text"]:
        type_hint = "auto"

    # 1. 读取文本
    print("正在读取...")
    raw_text = read_input(source, type_hint)
    if not raw_text:
        print("读取结果为空，请检查来源")
        return

    # 2. 清洗
    print("正在清洗文本...")
    cleaned = clean_text(raw_text)
    print(f"清洗后字符数：{len(cleaned)}")

    # 3. 关键词提取
    print("正在提取关键词...")
    keywords = extract_keywords(cleaned, topk=10)
    print("Top 10 关键词：", "、".join(keywords))

    # 4. 词云
    print("正在生成词云图片...")
    wordcloud_img = generate_wordcloud(keywords, "wordcloud.png")

    # 5. 初始化 LLM（使用 deepseek 平台，需要环境变量 DEEPSEEK_API_KEY）
    print("正在连接大模型...")
    llm = LLM("deepseek")

    # 6. 生成摘要
    print("正在生成三种摘要（可能需要几秒）...")
    summaries = generate_summaries(cleaned, llm)

    # 7. 输出到 summary.md
    output_file = "summary.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 文章摘要报告\n\n")
        f.write("## 关键词云\n\n")
        f.write(f"![词云]({wordcloud_img})\n\n")
        f.write(f"**Top10 关键词**：{', '.join(keywords)}\n\n")
        f.write("## 摘要\n\n")
        f.write("### 简短版（一句话）\n\n")
        f.write(f"{summaries['short']}\n\n")
        f.write("### 标准版（3-5句）\n\n")
        f.write(f"{summaries['medium']}\n\n")
        f.write("### 详细版（Q&A）\n\n")
        f.write(f"{summaries['long']}\n\n")
        f.write("---\n*生成时间：使用 DeepSeek 模型*\n")

    print(f"✅ 完成！结果已保存到 {output_file}，词云图片为 {wordcloud_img}")


if __name__ == '__main__':
    main()