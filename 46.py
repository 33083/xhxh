# smart_vocab.py
import random
import json
import csv
import sys
import os
import pymysql
from openai import OpenAI, APIConnectionError
from dotenv import load_dotenv
from config import DB_CONFIG, WORD_FILE, SCORE_CORRECT

# 解决 Windows 控制台中文乱码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# ==================== DeepSeek LLM 类（仅支持 DeepSeek） ====================
class LLM:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"          # 或者 "deepseek-v3"
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)
        self.temperature = 0.7

    def chat_non_stream(self, messages: list, max_tokens: int = 800):
        """流式调用，返回完整字符串"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"请求失败：{str(e)}"


# ==================== 智能背单词工具 ====================
class SmartVocabularyTool:
    def __init__(self):
        self.db_conn = None
        self.word_dict = []          # 列表元素: {"english": str, "chinese": str}
        self.wrong_words = []        # 本次会话错题本（存英文单词）
        self.current_score = 0       # 本次会话得分
        self.llm = LLM()             # 初始化 DeepSeek
        self._load_word_file()
        self._connect_db()
        self._load_score_from_db()

    # ---------- 1. 从文件加载单词库 ----------
    def _load_word_file(self):
        if not os.path.exists(WORD_FILE):
            print(f"⚠️ 单词文件 {WORD_FILE} 不存在，请创建后再运行。")
            sys.exit(1)

        if WORD_FILE.endswith(".csv"):
            with open(WORD_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.word_dict.append({
                        "english": row["english"].strip(),
                        "chinese": row["chinese"].strip()
                    })
        elif WORD_FILE.endswith(".json"):
            with open(WORD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    self.word_dict.append({
                        "english": item["english"],
                        "chinese": item["chinese"]
                    })
        else:
            raise ValueError("单词文件必须是 .csv 或 .json 格式")

        print(f"✅ 加载了 {len(self.word_dict)} 个单词")

    # ---------- 2. 数据库操作 ----------
    def _connect_db(self):
        try:
            self.db_conn = pymysql.connect(**DB_CONFIG)
            self.cursor = self.db_conn.cursor()
        except Exception as e:
            print(f"❌ 数据库连接失败：{e}")
            print("请检查 MySQL 服务是否启动，以及 config.py 中的用户名密码是否正确。")
            sys.exit(1)

    def _close_db(self):
        if self.db_conn:
            self.cursor.close()
            self.db_conn.close()

    def _load_score_from_db(self):
        self.cursor.execute("SELECT total_score FROM user_score WHERE id=1")
        row = self.cursor.fetchone()
        if row:
            self.current_score = row[0]
        else:
            self.current_score = 0

    def _save_score_to_db(self):
        self.cursor.execute("UPDATE user_score SET total_score = %s WHERE id=1", (self.current_score,))
        self.db_conn.commit()

    def _save_learning_record(self, word, chinese, user_input, is_correct, score_gained):
        sql = "INSERT INTO learning_records (word, chinese, user_input, is_correct, score_gained) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(sql, (word, chinese, user_input, is_correct, score_gained))
        self.db_conn.commit()

    def _update_wrong_book(self, word, chinese):
        """更新错题本：存在则增加错误次数，否则插入"""
        sql = """
            INSERT INTO wrong_books (word, chinese, wrong_count) 
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE 
                wrong_count = wrong_count + 1,
                last_wrong_time = CURRENT_TIMESTAMP
        """
        self.cursor.execute(sql, (word, chinese))
        self.db_conn.commit()

    def remove_from_wrong_book(self, word):
        """复习时答对，从错题本删除"""
        self.cursor.execute("DELETE FROM wrong_books WHERE word = %s", (word,))
        self.db_conn.commit()

    def get_all_wrong_words_from_db(self):
        """获取数据库中全部错题记录"""
        self.cursor.execute("SELECT word, chinese, wrong_count FROM wrong_books ORDER BY last_wrong_time DESC")
        return self.cursor.fetchall()

    # ---------- 3. 调用大模型生成例句和记忆技巧 ----------
    def generate_example_and_tip(self, word, chinese):
        """返回 (example_sentence, memory_tip)"""
        prompt = f"""请为英语单词 "{word}"（中文意思：{chinese}）生成：
1. 一个实用的英文例句（附带中文翻译）
2. 一个有趣的记忆技巧（谐音、联想、词根词缀等）

格式：
例句：...
记忆技巧：...
"""
        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm.chat_non_stream(messages, max_tokens=300)

        if response_text.startswith("请求失败"):
            # 降级为默认值
            return f"This is an example sentence with {word}.", f"Remember '{word}' by associating it with something familiar."

        # 解析返回内容
        example = ""
        tip = ""
        lines = response_text.split("\n")
        for line in lines:
            if line.startswith("例句："):
                example = line.replace("例句：", "").strip()
            elif line.startswith("记忆技巧："):
                tip = line.replace("记忆技巧：", "").strip()

        if not example:
            example = f"Example: I like {word}. (我喜欢{chinese})"
        if not tip:
            tip = "联想记忆法：关联到熟悉的场景"
        return example, tip

    # ---------- 4. 核心交互：随机抽词测验 ----------
    def quiz_once(self, use_wrong_mode=False):
        """
        use_wrong_mode = True 时，从错题本中抽词（复习模式）
        返回: 是否答对
        """
        if use_wrong_mode:
            wrong_list = self.get_all_wrong_words_from_db()
            if not wrong_list:
                print("\n🎉 恭喜！错题本已经清空，没有需要复习的单词了！")
                return True
            # 随机选一个错词
            word, chinese, count = random.choice(wrong_list)
            print(f"\n📖 [复习错题模式] 该词已错 {count} 次")
        else:
            if not self.word_dict:
                print("单词库为空")
                return False
            item = random.choice(self.word_dict)
            word, chinese = item["english"], item["chinese"]

        print(f"\n🀄️ 中文：{chinese}")
        user_input = input("✏️ 请输入对应的英文单词（输入 q 退出，输入 ? 查看提示）: ").strip()

        if user_input.lower() == 'q':
            print("退出本次练习。")
            self._close_db()
            sys.exit(0)

        if user_input.lower() == '?':
            # 调用大模型生成提示
            example, tip = self.generate_example_and_tip(word, chinese)
            print(f"\n💡 例句：{example}")
            print(f"🧠 记忆技巧：{tip}")
            # 再次让用户输入
            user_input = input("✏️ 再次输入英文: ").strip()
            if user_input.lower() == 'q':
                print("退出本次练习。")
                self._close_db()
                sys.exit(0)

        is_correct = (user_input.lower() == word.lower())
        score_gained = SCORE_CORRECT if is_correct else 0

        if is_correct:
            self.current_score += score_gained
            self._save_score_to_db()
            print(f"✅ 正确！ +{score_gained} 分，当前总分: {self.current_score}")
            if use_wrong_mode:
                self.remove_from_wrong_book(word)
                print(f"🎉 单词 '{word}' 已从错题本中移除！")
        else:
            print(f"❌ 错误！正确答案是: {word}")
            self.wrong_words.append(word)
            self._update_wrong_book(word, chinese)

        # 保存本次学习记录
        self._save_learning_record(word, chinese, user_input, is_correct, score_gained)

        # 如果答错，并且不是复习模式，调用大模型生成辅助信息
        if not is_correct and not use_wrong_mode:
            print("\n🔍 正在为你生成学习辅助...")
            example, tip = self.generate_example_and_tip(word, chinese)
            print(f"💡 例句：{example}")
            print(f"🧠 记忆技巧：{tip}")

        return is_correct

    # ---------- 5. 主循环 ----------
    def run(self):
        print("======= 智能背单词工具 =======")
        print("1. 开始普通练习")
        print("2. 只复习错题本")
        print("3. 查看当前总分")
        print("4. 退出")
        choice = input("请选择功能 (1/2/3/4): ")

        if choice == "1":
            self._practice_loop(use_wrong_mode=False)
        elif choice == "2":
            self._practice_loop(use_wrong_mode=True)
        elif choice == "3":
            print(f"🏆 您的当前总分: {self.current_score}")
            self.run()
        elif choice == "4":
            self._close_db()
            print("再见！")
            sys.exit(0)
        else:
            print("无效输入，请重新选择")
            self.run()

    def _practice_loop(self, use_wrong_mode=False):
        mode_name = "复习错题模式" if use_wrong_mode else "普通练习模式"
        print(f"\n开始{mode_name}，每次显示中文，输入英文。输入 q 退出，输入 ? 获取大模型提示。")
        while True:
            self.quiz_once(use_wrong_mode)
            cont = input("\n继续练习？(y/n): ").lower()
            if cont != 'y':
                break
        self.run()


# 启动程序
if __name__ == "__main__":
    tool = SmartVocabularyTool()
    try:
        tool.run()
    except KeyboardInterrupt:
        print("\n程序已退出")
        tool._close_db()