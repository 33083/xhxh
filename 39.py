from cryptography.fernet import Fernet
import os
import argparse
import sys

def encrypt_env_file(input_file, output_file, key_file):
    """加密 .env 文件，生成新密钥"""
    try:
        with open(input_file, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"错误：输入文件 '{input_file}' 不存在")
        sys.exit(1)

    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)
    print(f"密钥已保存至: {key_file} (请妥善保管)")

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(output_file, "wb") as f:
        f.write(encrypted)
    print(f"加密完成 → {output_file}")

def decrypt_env_file(enc_file, key_file, output_file):
    """解密文件，需要提供密钥文件"""
    try:
        with open(key_file, "rb") as f:
            key = f.read()
    except FileNotFoundError:
        print(f"错误：密钥文件 '{key_file}' 不存在")
        sys.exit(1)

    try:
        with open(enc_file, "rb") as f:
            encrypted = f.read()
    except FileNotFoundError:
        print(f"错误：加密文件 '{enc_file}' 不存在")
        sys.exit(1)

    try:
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted)
    except Exception as e:
        print(f"解密失败：密钥错误或文件损坏 -> {e}")
        sys.exit(1)

    with open(output_file, "wb") as f:
        f.write(decrypted)
    print(f"解密完成 → {output_file}")

if __name__ == "__main__":
    # 选择模式：加密或解密（二选一，注释掉另一个）
    
    # 模式1：加密 .env 文件
    encrypt_env_file("sxun\.env", "sxun\.env.enc", "secret.key")
    
    # 模式2：解密 .env.enc 文件（需要先有 secret.key）
    # decrypt_env_file(".env.enc", "secret.key", ".env")