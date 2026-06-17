# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL 配置（请修改为您的实际密码）
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",   # 改成你的 MySQL 密码
    "database": "word_db",
    "port": 3307,
    "charset": "utf8mb4"
}

# 单词库文件（支持 .csv 或 .json）
WORD_FILE = "words.csv"

# 答对得分
SCORE_CORRECT = 10