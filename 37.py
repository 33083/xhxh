from openai import OpenAI
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

    def chat(self, prompt: str):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            return f"网络连接失败：无法连接到 {self.platform} API，请检查网络连接或稍后重试。"
        except Exception as e:
            return f"请求失败：{str(e)}"

# 新增：记忆文件路径
MEMORY_FILE = "sxun/memory.json"
DEFAULT_ROLE = "你是一个专业的女秘书"

# 新增：加载记忆
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# 新增：保存记忆
def save_memory(memory):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# 新增：从文本中提取记忆信息
def extract_memory(text):
    mem = {}
    # 我叫/我是/我的名字是
    m = re.search(r"(?:我叫|我是|我的名字是|name is)\s*([\u4e00-\u9fa5a-zA-Z]+)", text)
    if m:
        mem["name"] = m.group(1)
    # 我喜欢/我爱
    m = re.search(r"(?:我喜欢|我爱|偏好)\s*([\u4e00-\u9fa5a-zA-Z0-9]+)", text)
    if m:
        mem["like"] = m.group(1)
    # 我住在/我在...城市
    m = re.search(r"(?:我住在|我在|来自)\s*([\u4e00-\u9fa5a-zA-Z]+)(?:市|省|区|家)", text)
    if m:
        mem["city"] = m.group(1)
    # 我的生日是/生日
    m = re.search(r"(?:生日|生于|出生)\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2})", text)
    if m:
        mem["birthday"] = m.group(1)
    return mem

# 新增：构建带记忆的system prompt
def build_system_prompt(role, memory):
    if not memory:
        return role
    mem_text = "\n以下是已知的用户信息，回答时优先参考：\n" + "\n".join([f"- {k}: {v}" for k, v in memory.items()])
    return role + mem_text

# 初始化全局变量
memory = load_memory()   # 加载已有记忆
current_role = DEFAULT_ROLE
# 构建初始system消息
system_content = build_system_prompt(current_role, memory)
messages = [{"role": "system", "content": system_content}]

# 日志函数（保持不变）
def write_log(msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs("sxun", exist_ok=True)
    with open("sxun/student_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {msg}\n")

def show_all_logs():
    try:
        with open("sxun/student_log.txt", "r", encoding="utf-8") as f:
            logs = f.read()
            if logs:
                print("\n========== 系统操作日志 ==========")
                print(logs)
                write_log("查看所有日志：成功")
            else:
                print("暂无日志记录")
    except FileNotFoundError:
        print("日志文件不存在，尚无操作记录")
    except Exception as e:
        print(f"读取日志失败: {e}")

def set_role():
    global messages, current_role, memory
    role_content = input("请输入角色设定: ")
    if role_content.strip() != "":
        current_role = role_content
        print(f"角色已设置为: {current_role}")
        write_log(f"角色已设置为: {current_role}")
    else:
        current_role = DEFAULT_ROLE
        print("使用默认角色: 你是一个专业的女秘书")
        write_log("使用默认角色")
    # 更新system消息（保留记忆）
    messages = [{"role": "system", "content": build_system_prompt(current_role, memory)}]

def dialog():
    global messages, memory, current_role
    # 确保system消息是最新的（角色+记忆）
    messages[0]["content"] = build_system_prompt(current_role, memory)
    print(f"\n当前角色: {current_role}")
    if memory:
        print("【已记住】", ", ".join([f"{k}:{v}" for k,v in memory.items()]))
    print("输入'退出'返回主菜单")
    while True:
        user_input = input("请输入: ")
        if user_input.strip() == "":
            print("请输入内容，不要留空")
            continue
        if user_input.lower() == "退出":
            write_log("用户退出对话模式")
            break

        # 新增：提取记忆并保存
        new_mem = extract_memory(user_input)
        if new_mem:
            memory.update(new_mem)
            save_memory(memory)
            # 更新system消息中的记忆部分
            messages[0]["content"] = build_system_prompt(current_role, memory)
            print(f"（已记住：{', '.join(new_mem.keys())}）")
            write_log(f"记住信息: {new_mem}")

        write_log(f"用户输入: {user_input}")
        messages.append({"role": "user", "content": user_input})
        stream = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=messages,
            stream=True,
            temperature=0.5
        )
        ans = ""
        print("助手回复:", end="")
        for chunk in stream:
            if chunk.choices[0].delta.content:
                ans += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="")
        print()
        write_log(f"助手回复: {ans}")
        messages.append({"role": "assistant", "content": ans})

while True:
    print("\n=== 聊天助手 ===")
    print("1.对话")
    print("2.清除对话")
    print("3.定义角色")
    print("4.退出")
    print("5.查看日志")
    choice = input("请输入选项: ")
    
    if choice == "1":
        print("1.deepseek")
        print("2.qwen")
        print("3.glm")
        platform = input("请输入平台: ")
        if platform == "1":
            llm = LLM("deepseek")
            a=input("请输入: ")
            print("DeepSeek:", llm.chat(a))
        elif platform == "2":
            llm = LLM("qwen")
            a=input("请输入: ")
            print("Qwen:", llm.chat(a))
        elif platform == "3":
            llm = LLM("glm")
            a=input("请输入: ")
            print("GLM:", llm.chat(a))
        else:
            print("无效平台，请输入1-3")
            continue
        dialog()
    elif choice == "2":
        # 清除对话历史，但保留system消息（包含角色和记忆）
        messages = [{"role": "system", "content": build_system_prompt(current_role, memory)}]
        print("对话已清除！")
        write_log("对话已清除")
    elif choice == "3":
        set_role()
    elif choice == "4":
        print("再见！")
        write_log("程序退出")
        break
    elif choice == "5":
        show_all_logs()
    else:
        print("无效选项，请输入1-5")