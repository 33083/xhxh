from cryptography.fernet import Fernet
from openai import OpenAI
from openai import APIConnectionError
from dotenv import load_dotenv
import os
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

class SecretManager:
    """密钥管理器，使用 Fernet 对称加密"""
    
    def __init__(self, key_file='secret.key'):
        self.key_file = key_file
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.key)
            print(f"[系统] 加密密钥已生成并保存至: {key_file}")
        self.fernet = Fernet(self.key)
    
    def encrypt_string(self, plain_text: str) -> str:
        """加密字符串，返回Base64编码的字符串"""
        encrypted = self.fernet.encrypt(plain_text.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """解密Base64编码的字符串"""
        return self.fernet.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
    
    def save_secret(self, name: str, value: str, secrets_file='secrets.json'):
        """保存加密后的密钥"""
        encrypted_value = self.encrypt_string(value)
        if os.path.exists(secrets_file):
            with open(secrets_file, 'r', encoding='utf-8') as f:
                secrets = json.load(f)
        else:
            secrets = {}
        secrets[name] = encrypted_value
        with open(secrets_file, 'w', encoding='utf-8') as f:
            json.dump(secrets, f, indent=2)
    
    def load_secret(self, name: str, secrets_file='secrets.json') -> str:
        """加载并解密密钥"""
        if not os.path.exists(secrets_file):
            return None
        with open(secrets_file, 'r', encoding='utf-8') as f:
            secrets = json.load(f)
        if name not in secrets:
            return None
        return self.decrypt_string(secrets[name])

class LLM:
    """多平台 LLM 调用工具，支持密钥加密存储"""
    
    PLATFORMS = {
        "deepseek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-v4-pro"},
        "qwen": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus"},
        "glm": {"base_url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4"},
        "spark": {"base_url": "https://spark-api-open.xf-yun.com/v2", "model": "spark-x"},
    }

    def __init__(self, platform: str, api_key: str = None):
        if platform not in self.PLATFORMS:
            raise ValueError(f"不支持的平台: {platform}")
        
        config = self.PLATFORMS[platform]
        
        if api_key is None:
            sm = SecretManager()
            env_key = f"{platform.upper()}_API_KEY"
            api_key = sm.load_secret(env_key)
            if api_key is None:
                api_key = os.getenv(env_key)
        
        if api_key is None:
            raise ValueError(f"未找到 {platform} 的 API 密钥")
        
        self.client = OpenAI(api_key=api_key, base_url=config["base_url"])
        self.model = config["model"]
        self.temperature = 0.5
        self.platform = platform

    def chat(self, messages, stream=True):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                temperature=self.temperature,
            )
            if stream:
                return response
            else:
                return response.choices[0].message.content
        except APIConnectionError as e:
            return f"网络连接失败：无法连接到 {self.platform} API"
        except Exception as e:
            return f"请求失败：{str(e)}"

LOG_FILE = "student_log.txt"
CURRENT_ROLE = "你是一个专业的助手，善于倾听并提供有帮助的回答。"

def write_log(msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {msg}\n")

def show_all_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.read()
            if logs:
                print("\n" + "="*60)
                print("系统操作日志")
                print("="*60)
                print(logs)
                print("="*60)
            else:
                print("暂无日志记录")
    except FileNotFoundError:
        print("日志文件不存在")
    except Exception as e:
        print(f"读取日志失败: {e}")

def set_role():
    global CURRENT_ROLE
    print("\n" + "="*50)
    print("角色设定")
    print("="*50)
    print(f"当前角色: {CURRENT_ROLE}")
    new_role = input("请输入新的角色设定: ").strip()
    if new_role:
        CURRENT_ROLE = new_role
        print(f"\n✓ 角色已更新为: {CURRENT_ROLE}")
        write_log(f"角色更新为: {CURRENT_ROLE}")
    else:
        print("未输入角色设定，保持原有角色")

def setup_secrets():
    sm = SecretManager()
    print("\n" + "="*50)
    print("API 密钥加密配置")
    print("="*50)
    
    platforms = list(LLM.PLATFORMS.keys())
    env_file = ".env"
    
    for platform in platforms:
        secret_name = f"{platform.upper()}_API_KEY"
        api_key = os.getenv(secret_name)
        
        if api_key:
            print(f"检测到 {platform} 的密钥，正在加密保存...")
            sm.save_secret(secret_name, api_key)
            print(f"✓ {platform} 密钥已加密保存")
        else:
            api_key_input = input(f"请输入 {platform} 的 API Key（按回车跳过）: ").strip()
            if api_key_input:
                sm.save_secret(secret_name, api_key_input)
                print(f"✓ {platform} 密钥已加密保存")
    
    print("="*50)
    write_log("完成 API 密钥加密配置")

def select_platform():
    print("\n选择 LLM 平台:")
    platforms = list(LLM.PLATFORMS.keys())
    for i, p in enumerate(platforms, 1):
        print(f"{i}. {p}")
    while True:
        choice = input("请输入平台编号: ")
        if choice.isdigit() and 1 <= int(choice) <= len(platforms):
            return platforms[int(choice)-1]
        print("无效输入，请重新选择")

def chat_interface():
    messages = [{"role": "system", "content": CURRENT_ROLE}]
    
    print("\n" + "="*50)
    print("欢迎使用 LLM 聊天助手")
    print(f"当前角色: {CURRENT_ROLE}")
    print("="*50)
    
    platform = select_platform()
    try:
        llm = LLM(platform)
        print(f"\n已连接到 {platform} 平台")
        write_log(f"连接到 {platform} 平台")
    except Exception as e:
        print(f"连接失败: {e}")
        return
    
    while True:
        user_input = input("\n你: ")
        
        if user_input.lower() == "退出":
            write_log("用户退出对话")
            print("再见！")
            break
        
        if not user_input.strip():
            print("请输入内容")
            continue
        
        write_log(f"用户输入: {user_input}")
        messages.append({"role": "user", "content": user_input})
        
        print(f"\n{platform}:", end="")
        ans = ""
        try:
            stream = llm.chat(messages)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    ans += content
                    print(content, end="", flush=True)
            print()
        except Exception as e:
            ans = str(e)
            print(ans)
        
        write_log(f"助手回复: {ans}")
        messages.append({"role": "assistant", "content": ans})
        
        if len(messages) > 20:
            messages = messages[:1] + messages[-19:]

def main():
    while True:
        print("\n" + "="*50)
        print("LLM 多平台聊天助手 (Fernet加密)")
        print("="*50)
        print("1. 开始对话")
        print("2. 配置 API 密钥（加密保存）")
        print("3. 设置角色")
        print("4. 查看操作日志")
        print("5. 退出")
        print("="*50)
        
        choice = input("请输入选项 (1-5): ")
        
        if choice == "1":
            chat_interface()
        elif choice == "2":
            setup_secrets()
        elif choice == "3":
            set_role()
        elif choice == "4":
            show_all_logs()
        elif choice == "5":
            print("感谢使用，再见！")
            write_log("程序退出")
            break
        else:
            print("无效选项，请输入 1-5")

if __name__ == "__main__":
    main()