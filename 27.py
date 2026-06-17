# import pymysql

# # 数据库连接配置
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '123456',
#     'database': 'company',
#     'port': 3307,
#     'charset': 'utf8mb4'
# }

# def get_connection():
#     """获取数据库连接"""
#     return pymysql.connect(**DB_CONFIG)

# def create_table():
#     """创建 user 表（如果不存在）"""
#     conn = None
#     cursor = None
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         sql = '''
#         CREATE TABLE IF NOT EXISTS user (
#             id INT PRIMARY KEY AUTO_INCREMENT,
#             username VARCHAR(50) NOT NULL,
#             password VARCHAR(50) NOT NULL,
#             phone VARCHAR(20),
#             gender CHAR(1) COMMENT 'M:男 F:女'
#         )
#         '''
#         cursor.execute(sql)
#         conn.commit()
#         print("表 user 已准备就绪")
#     except pymysql.MySQLError as e:
#         print(f"创建表失败: {e}")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# def insert_user():
#     """插入一条新用户（从控制台输入）"""
#     conn = None
#     cursor = None
#     try:
#         print("\n--- 插入新用户 ---")
#         username = input("请输入用户名: ").strip()
#         password = input("请输入密码: ").strip()
#         phone = input("请输入手机号: ").strip()
#         gender = input("请输入性别 (M/F): ").strip().upper()
#         if gender not in ('M', 'F'):
#             print("性别只能是 M 或 F")
#             return

#         conn = get_connection()
#         cursor = conn.cursor()
#         sql = "INSERT INTO user (username, password, phone, gender) VALUES (%s, %s, %s, %s)"
#         cursor.execute(sql, (username, password, phone, gender))
#         conn.commit()
#         print(f"成功插入 {cursor.rowcount} 条记录，新ID: {cursor.lastrowid}")
#     except pymysql.MySQLError as e:
#         print(f"插入失败: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# def query_users():
#     """查询用户，可按性别过滤，也可以查询所有"""
#     conn = None
#     cursor = None
#     try:
#         print("\n--- 查询用户 ---")
#         print("1. 查询所有用户")
#         print("2. 按性别查询 (M/F)")
#         sub = input("请选择: ").strip()
#         conn = get_connection()
#         cursor = conn.cursor()
#         if sub == '1':
#             sql = "SELECT id, username, phone, gender FROM user"
#             cursor.execute(sql)
#         elif sub == '2':
#             gender = input("请输入性别 (M/F): ").strip().upper()
#             if gender not in ('M', 'F'):
#                 print("性别无效")
#                 return
#             sql = "SELECT id, username, phone, gender FROM user WHERE gender = %s"
#             cursor.execute(sql, (gender,))
#         else:
#             print("无效选择")
#             return

#         rows = cursor.fetchall()
#         if not rows:
#             print("没有找到任何用户")
#         else:
#             print("\nID\t用户名\t手机号\t\t性别")
#             for row in rows:
#                 print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}")
#     except pymysql.MySQLError as e:
#         print(f"查询失败: {e}")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# def update_user():
#     """更新用户信息（手机号或密码）"""
#     conn = None
#     cursor = None
#     try:
#         print("\n--- 更新用户信息 ---")
#         uid = input("请输入要更新的用户ID: ").strip()
#         if not uid.isdigit():
#             print("ID必须是数字")
#             return
#         uid = int(uid)

#         print("1. 更新手机号")
#         print("2. 更新密码")
#         choice = input("请选择: ").strip()
#         if choice == '1':
#             new_phone = input("请输入新手机号: ").strip()
#             sql = "UPDATE user SET phone = %s WHERE id = %s"
#             params = (new_phone, uid)
#         elif choice == '2':
#             new_pwd = input("请输入新密码: ").strip()
#             sql = "UPDATE user SET password = %s WHERE id = %s"
#             params = (new_pwd, uid)
#         else:
#             print("无效选择")
#             return

#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute(sql, params)
#         conn.commit()
#         if cursor.rowcount > 0:
#             print(f"成功更新 {cursor.rowcount} 条记录")
#         else:
#             print("没有找到该ID的用户，更新失败")
#     except pymysql.MySQLError as e:
#         print(f"更新失败: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# def delete_user():
#     """删除用户（根据ID）"""
#     conn = None
#     cursor = None
#     try:
#         print("\n--- 删除用户 ---")
#         uid = input("请输入要删除的用户ID: ").strip()
#         if not uid.isdigit():
#             print("ID必须是数字")
#             return
#         uid = int(uid)
#         conn = get_connection()
#         cursor = conn.cursor()
#         sql = "DELETE FROM user WHERE id = %s"
#         cursor.execute(sql, (uid,))
#         conn.commit()
#         if cursor.rowcount > 0:
#             print(f"成功删除 {cursor.rowcount} 条记录")
#         else:
#             print("没有找到该ID的用户")
#     except pymysql.MySQLError as e:
#         print(f"删除失败: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# def main():
#     """主菜单循环"""
#     # 确保表存在
#     create_table()

#     while True:
#         print("\n========== 用户管理系统 ==========")
#         print("1. 插入用户")
#         print("2. 查询用户")
#         print("3. 更新用户")
#         print("4. 删除用户")
#         print("5. 退出")
#         choice = input("请输入您的选择: ").strip()
#         if choice == '1':
#             insert_user()
#         elif choice == '2':
#             query_users()
#         elif choice == '3':
#             update_user()
#         elif choice == '4':
#             delete_user()
#         elif choice == '5':
#             print("退出程序")
#             break
#         else:
#             print("无效选择，请重新输入")

# if __name__ == '__main__':
#     main()
# class UserManager:
#     """用户管理类，依赖 DBHelper 实现针对 user 表的扩展操作"""
    
#     def __init__(self, db_helper):
#         """
#         构造方法，接收一个 DBHelper 实例作为依赖
#         同时确保 user 表中存在 email 字段
#         """
#         self.db = db_helper
#         self._ensure_email_column()
    
#     def _ensure_email_column(self):
#         """检查并添加 email 列（如果不存在）"""
#         if not self.db._connect():
#             raise Exception("数据库连接失败，无法检查表结构")
#         try:
#             # 检查 email 列是否存在
#             self.db.cursor.execute("SHOW COLUMNS FROM user LIKE 'email'")
#             result = self.db.cursor.fetchone()
#             if not result:
#                 # 添加 email 列
#                 self.db.cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(100) DEFAULT NULL")
#                 self.db.conn.commit()
#                 print("已为 user 表添加 email 字段")
#         except Exception as e:
#             print(f"检查/添加 email 列失败: {e}")
#             self.db.conn.rollback()
#         finally:
#             self.db._close()
    
#     def add_user(self, username, password, phone, gender, email=None):
#         """
#         添加新用户
#         :param username: 用户名
#         :param password: 密码
#         :param phone: 手机号
#         :param gender: 性别 ('M' 或 'F')
#         :param email: 邮箱 (可选)
#         :return: 插入成功返回 True，失败返回 False
#         """
#         if not self.db._connect():
#             return False
#         try:
#             sql = """
#                 INSERT INTO user (username, password, phone, gender, email)
#                 VALUES (%s, %s, %s, %s, %s)
#             """
#             self.db.cursor.execute(sql, (username, password, phone, gender, email))
#             self.db.conn.commit()
#             print(f"用户 {username} 添加成功，ID: {self.db.cursor.lastrowid}")
#             return True
#         except Exception as e:
#             print(f"添加用户失败: {e}")
#             self.db.conn.rollback()
#             return False
#         finally:
#             self.db._close()
    
#     def get_user_by_id(self, user_id):
#         """
#         根据用户 ID 查询完整信息
#         :param user_id: 用户 ID
#         :return: 用户信息字典，若未找到则返回 None
#         """
#         if not self.db._connect():
#             return None
#         try:
#             sql = "SELECT id, username, password, phone, gender, email FROM user WHERE id = %s"
#             self.db.cursor.execute(sql, (user_id,))
#             row = self.db.cursor.fetchone()
#             if row:
#                 # 将查询结果转换为字典，方便调用
#                 columns = ['id', 'username', 'password', 'phone', 'gender', 'email']
#                 user_dict = dict(zip(columns, row))
#                 return user_dict
#             else:
#                 print(f"未找到 ID 为 {user_id} 的用户")
#                 return None
#         except Exception as e:
#             print(f"查询用户失败: {e}")
#             return None
#         finally:
#             self.db._close()
    
#     def update_user_email(self, user_id, new_email):
#         """
#         更新指定用户的邮箱地址
#         :param user_id: 用户 ID
#         :param new_email: 新邮箱
#         :return: 更新成功返回 True，失败返回 False
#         """
#         if not self.db._connect():
#             return False
#         try:
#             sql = "UPDATE user SET email = %s WHERE id = %s"
#             self.db.cursor.execute(sql, (new_email, user_id))
#             self.db.conn.commit()
#             if self.db.cursor.rowcount > 0:
#                 print(f"用户 {user_id} 的邮箱已更新为 {new_email}")
#                 return True
#             else:
#                 print(f"未找到 ID 为 {user_id} 的用户，更新失败")
#                 return False
#         except Exception as e:
#             print(f"更新邮箱失败: {e}")
#             self.db.conn.rollback()
#             return False
#         finally:
#             self.db._close()
    
#     def delete_user(self, user_id):
#         """
#         删除指定用户
#         :param user_id: 用户 ID
#         :return: 删除成功返回 True，失败返回 False
#         """
#         # 直接复用 DBHelper 中已有的 delete_user 方法
#         return self.db.delete_user(user_id)
# if __name__ == '__main__':
#     # 创建 DBHelper 实例并初始化表
#     db = DBHelper(host='localhost', user='root', password='123456', database='company', port=3307)
#     db.create_table()
    
#     # 创建 UserManager，注入 DBHelper 依赖
#     user_manager = UserManager(db)
    
#     # 添加用户（带邮箱）
#     user_manager.add_user('张三', 'zhang123', '13800138000', 'M', 'zhangsan@example.com')
    
#     # 根据 ID 查询用户
#     user = user_manager.get_user_by_id(1)
#     print(user)
    
#     # 更新邮箱
#     user_manager.update_user_email(1, 'newemail@example.com')
    
#     # 删除用户
#     user_manager.delete_user(1)
# init_db.py
import pymysql
from config import DB_CONFIG

def init_database():
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
        charset="utf8mb4"
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")

    # 学习记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            word VARCHAR(100) NOT NULL,
            chinese VARCHAR(200) NOT NULL,
            user_input VARCHAR(100),
            is_correct BOOLEAN,
            score_gained INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 错题本表（独立记录错题，便于复习）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wrong_books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            word VARCHAR(100) NOT NULL,
            chinese VARCHAR(200) NOT NULL,
            wrong_count INT DEFAULT 1,
            last_wrong_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_word (word)
        )
    """)

    # 用户总分表（简单持久化总分）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_score (
            id INT PRIMARY KEY DEFAULT 1,
            total_score INT DEFAULT 0
        )
    """)
    cursor.execute("INSERT IGNORE INTO user_score (id, total_score) VALUES (1, 0)")

    conn.commit()
    cursor.close()
    conn.close()
    print("数据库初始化完成")

if __name__ == "__main__":
    init_database()