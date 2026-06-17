from cryptography.fernet import Fernet
from openai import OpenAI
from openai import APIConnectionError
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

class SecretManager:
    """密钥管理器，支持密钥持久化、字符串/字节数据加解密"""
    
    def __init__(self, key_file='llm_secret.key'):
        """
        初始化密钥管理器。
        :param key_file: 密钥文件路径，如果文件存在则加载，否则生成新密钥并保存。
        """
        self.key_file = key_file
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            self._save_key()
            print(f"新密钥已生成并保存至: {key_file}")
        self.fernet = Fernet(self.key)
    
    def _save_key(self):
        """将密钥保存到文件"""
        with open(self.key_file, 'wb') as f:
            f.write(self.key)
    
    def encrypt(self, data):
        """加密数据（字符串或字节）"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.fernet.encrypt(data)
    
    def decrypt(self, encrypted_data):
        """解密数据"""
        return self.fernet.decrypt(encrypted_data)
    
    def encrypt_string(self, plain_text: str) -> bytes:
        """加密字符串，返回加密后的字节串"""
        return self.encrypt(plain_text)
    
    def decrypt_string(self, encrypted_data: bytes) -> str:
        """解密字节串为字符串"""
        return self.decrypt(encrypted_data).decode('utf-8')
    
    def save_secret(self, secret_name: str, secret_value: str, secrets_file='secrets.json'):
        """保存加密后的密钥到 JSON 文件"""
        encrypted_value = self.encrypt_string(secret_value).decode('utf-8')
        
        if os.path.exists(secrets_file):
            with open(secrets_file, 'r', encoding='utf-8') as f:
                secrets = json.load(f)
        else:
            secrets = {}
        
        secrets[secret_name] = encrypted_value
        
        with open(secrets_file, 'w', encoding='utf-8') as f:
            json.dump(secrets, f, indent=2)
        
        print(f"密钥 '{secret_name}' 已加密保存")
    
    def load_secret(self, secret_name: str, secrets_file='secrets.json') -> str:
        """从 JSON 文件加载并解密密钥"""
        if not os.path.exists(secrets_file):
            raise FileNotFoundError(f"密钥文件 {secrets_file} 不存在")
        
        with open(secrets_file, 'r', encoding='utf-8') as f:
            secrets = json.load(f)
        
        if secret_name not in secrets:
            raise KeyError(f"密钥 '{secret_name}' 不存在于 {secrets_file}")
        
        encrypted_value = secrets[secret_name]
        return self.decrypt_string(encrypted_value.encode('utf-8'))

class LLM:
    """多平台 LLM 调用工具，支持 API 密钥加密存储"""
    
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
            "base_url": "https://spark-api-open.xf-yun.com/v2",
            "model": "spark-x",
        },
    }

    def __init__(self, platform: str, api_key: str = None, secret_manager: SecretManager = None):
        if platform not in self.PLATFORMS:
            raise ValueError(f"不支持的平台: {platform}。支持的平台: {list(self.PLATFORMS.keys())}")
        
        config = self.PLATFORMS[platform]
        
        if api_key is None:
            if secret_manager is None:
                secret_manager = SecretManager()
            
            env_key = f"{platform.upper()}_API_KEY"
            try:
                api_key = secret_manager.load_secret(env_key)
            except (FileNotFoundError, KeyError):
                api_key = os.getenv(env_key)
                if api_key is None:
                    raise ValueError(f"未找到 {platform} 的 API 密钥，请通过参数传入或配置环境变量/{secret_manager}")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=config["base_url"],
        )
        self.model = config["model"]
        self.temperature = 0.5
        self.platform = platform
        self.secret_manager = secret_manager

    def chat(self, prompt: str, temperature: float = None):
        """
        调用 LLM 进行对话
        :param prompt: 用户输入的提示词
        :param temperature: 温度参数，控制输出的随机性
        :return: 模型返回的响应内容
        """
        try:
            temp = temperature if temperature is not None else self.temperature
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            return f"网络连接失败：无法连接到 {self.platform} API，请检查网络连接或稍后重试。"
        except Exception as e:
            return f"请求失败：{str(e)}"

def setup_secrets():
    """交互式设置并加密保存所有平台的 API 密钥"""
    sm = SecretManager()
    
    print("=== API 密钥加密配置向导 ===")
    print("请输入各平台的 API 密钥（按回车跳过）")
    print("-" * 40)
    
    platforms = ["deepseek", "qwen", "glm", "spark", "hunyuan"]
    
    for platform in platforms:
        api_key = input(f"请输入 {platform} 的 API Key: ").strip()
        if api_key:
            secret_name = f"{platform.upper()}_API_KEY"
            sm.save_secret(secret_name, api_key)
    
    print("-" * 40)
    print("所有密钥已加密保存完成！")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="多平台 LLM 调用工具（支持密钥加密）")
    parser.add_argument("--setup", action="store_true", help="配置并加密保存 API 密钥")
    parser.add_argument("--platform", "-p", help="选择平台: deepseek/qwen/glm/spark/hunyuan")
    parser.add_argument("--prompt", "-q", help="输入问题")
    parser.add_argument("--temp", "-t", type=float, default=0.5, help="温度参数 (0-1)")
    
    args = parser.parse_args()
    
    if args.setup:
        setup_secrets()
    elif args.platform and args.prompt:
        sm = SecretManager()
        try:
            llm = LLM(args.platform, secret_manager=sm)
            response = llm.chat(args.prompt, args.temp)
            print(f"\n{args.platform.capitalize()} 响应:")
            print("-" * 50)
            print(response)
            print("-" * 50)
        except Exception as e:
            print(f"错误: {e}")
    else:
        print("=== LLM 多平台调用工具 ===")
        print("使用方法:")
        print("  1. 配置密钥: python llm_secret_manager.py --setup")
        print("  2. 调用模型: python llm_secret_manager.py -p <平台> -q <问题>")
        print("支持平台: deepseek, qwen, glm, spark, hunyuan")
        print("\n示例:")
        print('  python llm_secret_manager.py -p deepseek -q "你好"')