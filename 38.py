# import sys
# sys.stdout.reconfigure(encoding='utf-8')

# from openai import OpenAI
# from openai import APIConnectionError
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class LLM:
#     PLATFORMS = {
#         "deepseek": {
#             "base_url": "https://api.deepseek.com/v1",
#             "model": "deepseek-v4-pro",
#         },
#         "qwen": {
#             "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
#             "model": "qwen-plus",
#         },
#         "glm": {
#             "base_url": "https://open.bigmodel.cn/api/paas/v4",
#             "model": "glm-4",
#         },
#         "spark": {
#             "base_url": "https://spark-api-open.xf-yun.com/x2/",
#             "model": "spark-x",
#         } 
#     }

#     def __init__(self, platform: str, api_key: str = None):
#         config = self.PLATFORMS[platform]
#         if api_key is None:
#             api_key = os.getenv(f"{platform.upper()}_API_KEY")
#         self.client = OpenAI(
#             api_key=api_key,
#             base_url=config["base_url"],
#         )
#         self.model = config["model"]
#         self.temperature = 0.5
#         self.platform = platform

#     def chat(self, prompt: str):
#         """流式生成器：逐块返回内容"""
#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=self.temperature,
#                 stream=True,
#             )
#         except APIConnectionError as e:
#             yield f"网络连接失败：无法连接到 {self.platform} API，请检查网络连接或稍后重试。"
#             return
#         except Exception as e:
#             yield f"请求失败：{str(e)}"
#             return

#         for chunk in response:
#             delta = chunk.choices[0].delta
#             content = delta.content if delta and delta.content else ""
#             if content:
#                 yield content


# if __name__ == "__main__":
#     a = input("请输入: ")
   
#     # 正确使用流式：遍历生成器并实时输出
#     llm = LLM("qwen")
#     print("Qwen: ", end="", flush=True)
#     for piece in llm.chat(a):
#         print(piece, end="", flush=True)
#     print()

#     llm = LLM("glm")
#     print("GLM: ", end="", flush=True)
#     for piece in llm.chat(a):
#         print(piece, end="", flush=True)
#     print()

#     llm = LLM("spark")
#     print("Spark: ", end="", flush=True)
#     for piece in llm.chat(a):
#         print(piece, end="", flush=True)
#     print()

#     # 收集完整回答用于 deepseek 的 prompt
#     b = "".join([p for p in LLM("spark").chat(a)])
#     c = "".join([p for p in LLM("glm").chat(a)])
#     d = "".join([p for p in LLM("qwen").chat(a)])

#     llm = LLM("deepseek")
#     print("DeepSeek: ", end="", flush=True)
#     for piece in llm.chat(f"直接告诉我哪个观点更好：{b},{c},{d}"):
#         print(piece, end="", flush=True)
#     print()
import sys
import os
from datetime import datetime
from openai import OpenAI
from openai import APIConnectionError
from dotenv import load_dotenv

# 设置控制台 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# ==================== 您原有的 LLM 类（稍作扩展，增加流式） ====================
class LLM:
    PLATFORMS = {
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",          # 模型名请确认，如有问题改为 deepseek-v3 等
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

    def chat_non_stream(self, messages: list, max_tokens: int = 800):
        """非流式调用，返回完整字符串（用于裁判）"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"请求失败：{str(e)}"


# ==================== 辩手类（直接封装 LLM） ====================
class Debater:
    def __init__(self, name: str, platform: str):
        self.name = name
        self.llm = LLM(platform)

    def speak(self, topic: str, history: list, max_tokens: int = 300):
        """
        根据辩题和对话历史生成发言（流式生成器）
        history: 每条格式 "发言人: 内容"
        """
        # 构建系统提示
        system_prompt = f"你是一位辩手，名叫{self.name}。请针对当前辩题发表观点，可以反驳或赞同之前发言者。每轮发言控制在200字以内。"
        # 组装消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"本次辩题：{topic}"}
        ]
        # 加入历史对话
        for h in history:
            messages.append({"role": "user", "content": h})
        # 提示当前发言者
        messages.append({"role": "user", "content": f"现在轮到{self.name}发言，请开始："})
        
        return self.llm.chat_stream(messages, max_tokens=max_tokens)


# ==================== 裁判类 ====================
class Judge:
    def __init__(self, name: str = "裁判长", platform: str = "deepseek"):
        self.name = name
        self.llm = LLM(platform)

    def evaluate(self, topic: str, debate_log: list) -> str:
        """对辩论记录进行评分和总结"""
        transcript = "\n".join(debate_log)
        prompt = f"""你是一位公正的辩论裁判。请对下面这场关于“{topic}”的辩论进行评分和总结。

辩论记录：
{transcript}

请输出：
1. 每位辩手的表现评分（百分制）及简短评语。
2. 最终获胜方（哪位辩手说服力最强）。
3. 总体评价与建议。

注意：评分要客观，点评要有依据。"""
        messages = [
            {"role": "system", "content": "你是一位资深辩论裁判，擅长分析和评分。"},
            {"role": "user", "content": prompt}
        ]
        return self.llm.chat_non_stream(messages, max_tokens=800)


# ==================== 主程序 ====================
def main():
    # 用户输入辩题
    topic = input("请输入辩题：").strip()
    if not topic:
        topic = "人工智能是否最终会取代人类大部分工作？"
        print(f"使用默认辩题：{topic}")

    # 定义三位辩手（顺序固定）
    debaters = [
        Debater("通义千问", "qwen"),
        Debater("智谱GLM", "glm"),
        Debater("讯飞星火", "spark"),
    ]
    judge = Judge("DeepSeek裁判", "deepseek")

    # 存储辩论记录（纯文本，每行格式 "轮数-发言人: 内容"）
    debate_log = []
    full_history = []   # 格式 "发言人: 内容"，供下一轮使用

    print("\n========== 辩论开始 ==========")
    start_time = datetime.now()

    # 循环 3 轮
    for round_num in range(1, 4):
        print(f"\n--- 第 {round_num} 轮 ---")
        for debater in debaters:
            print(f"\n{debater.name} 发言：", end=" ", flush=True)
            # 流式输出并收集完整回复
            full_response = ""
            for chunk in debater.speak(topic, full_history):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()  # 换行
            
            # 记录
            log_entry = f"第{round_num}轮-{debater.name}: {full_response}"
            debate_log.append(log_entry)
            full_history.append(f"{debater.name}: {full_response}")

    # 裁判打分
    print("\n========== 裁判评分 ==========")
    print("裁判长（DeepSeek）正在评估...")
    judge_comment = judge.evaluate(topic, debate_log)
    print("\n【裁判长点评】\n", judge_comment)
    debate_log.append(f"裁判长: {judge_comment}")

    # 保存文件
    filename = f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"辩题：{topic}\n")
        f.write(f"辩论开始时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        for line in debate_log:
            f.write(line + "\n")
        f.write("=" * 60 + "\n")
        f.write(f"裁判总结：\n{judge_comment}\n")
    print(f"\n辩论记录已保存至：{filename}")


if __name__ == "__main__":
    main()