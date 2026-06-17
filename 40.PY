from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

class SecretManager:
    """密钥管理器，支持密钥持久化、字符串/字节数据加解密"""
    
    def __init__(self, key_file='key.key'):
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
        self.fernet = Fernet(self.key)
    
    def _save_key(self):
        """将密钥保存到文件（权限建议设为600，但跨平台可省略）"""
        with open(self.key_file, 'wb') as f:
            f.write(self.key)
        # 可选：设置文件权限（仅限Unix）
        # os.chmod(self.key_file, 0o600)
    
    def encrypt(self, data):
        """
        加密数据（字符串或字节）。
        :param data: 字符串（将自动编码为utf-8）或字节数据
        :return: 加密后的字节串
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.fernet.encrypt(data)
    
    def decrypt(self, encrypted_data):
        """
        解密数据。
        :param encrypted_data: 加密后的字节串
        :return: 解密后的字节串
        """
        return self.fernet.decrypt(encrypted_data)
    
    def encrypt_string(self, plain_text: str) -> bytes:
        """加密字符串，返回加密后的字节串"""
        return self.encrypt(plain_text)
    
    def decrypt_string(self, encrypted_data: bytes) -> str:
        """解密字节串为字符串"""
        return self.decrypt(encrypted_data).decode('utf-8')
    
    def encrypt_file(self, input_file: str, output_file: str = None):
        """
        加密文件。
        :param input_file: 要加密的源文件路径
        :param output_file: 加密后的输出文件路径，默认在源文件名后加 .enc
        """
        if output_file is None:
            output_file = input_file + '.enc'
        with open(input_file, 'rb') as f:
            plain_data = f.read()
        encrypted_data = self.encrypt(plain_data)
        with open(output_file, 'wb') as f:
            f.write(encrypted_data)
        print(f"文件加密完成：{output_file}")
    
    def decrypt_file(self, input_file: str, output_file: str = None):
        """
        解密文件。
        :param input_file: 加密文件路径
        :param output_file: 解密后的输出文件路径，默认去除 .enc 后缀（若存在）
        """
        if output_file is None:
            if input_file.endswith('.enc'):
                output_file = input_file[:-4]
            else:
                output_file = input_file + '.dec'
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = self.decrypt(encrypted_data)
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)
        print(f"文件解密完成：{output_file}")

# 使用示例
if __name__ == '__main__':
    # 创建实例（首次运行会生成 key.key 文件，之后复用）
    sm = SecretManager('my_secret.key')
    
    # 字符串加解密
    # secret_msg = ""
    # encrypted = sm.encrypt_string(secret_msg)
    # print(f"加密后: {encrypted}")
    # decrypted = sm.decrypt_string(encrypted)
    # print(f"解密后: {decrypted}")
    
    #文件加解密（示例）
    sm.encrypt_file('.env')
    sm.decrypt_file('.env.enc')