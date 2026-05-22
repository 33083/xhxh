# 图书馆管理系统
import pymysql
import time
class bookManager:
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",          
                password="123456",    
                database="book_db",
                charset="utf8mb4",
                port=3307,
                autocommit=False
            )
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            print(" 数据库连接成功")
        except Exception as e:
            print(" 数据库连接失败：", e)
    
    # 日志
    def write_log(self, msg):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with open("sxun/student_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] {msg}\n")
    
    # 查看日志
    def show_all_logs(self):
        try:
            with open("sxun/student_log.txt", "r", encoding="utf-8") as f:
                logs = f.read()
                if logs:
                    print("\n========== 系统操作日志 ==========")
                    print(logs)
                    self.write_log("查看所有日志：成功")
                else:
                    print("暂无日志记录")
        except FileNotFoundError:
            print("日志文件不存在，尚无操作记录")
        except Exception as e:
            print(f"读取日志失败: {e}")
    # 添加书籍
    def add_book(self, book_id, book_name, name, major):
        try:
            sql = "INSERT INTO book(book_id, book_name, name,major,state) VALUES(%s,%s,%s,%s,%s)"
            self.cursor.execute(sql, (book_id, book_name, name,major,'可借阅'))
            self.conn.commit()
            print("图书添加成功")
            self.write_log(f"添加图书：{book_id} {book_name} {name} {major}")
        except Exception as e:
            self.conn.rollback()
            print("添加失败！学号重复或数据格式错误")
    def show_all_book(self):
        sql = """
        SELECT b.book_id, b.book_name,b.name, b.major, b.state  FROM book b
        """
        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        if not res:
            print("暂无书籍数据！")
            self.write_log("查询所有书籍数据：暂无书籍数据")
            return
        print("\n========== 图书信息 ==========")
        for item in res:
            print(f"书籍编号：{item['book_id']} | 书名：{item['book_name']} | 作者：{item['name']} | 分类：{item['major']} | 状态：{item['state']}")
        self.write_log("查询所有书籍数据：成功")
    
    # 按编号查找
    def search_id(self, book_id):
        sql = """
        SELECT b.book_id, b.book_name,b.name, b.major, b.state
        FROM book b
        WHERE b.book_id = %s
        """
        self.cursor.execute(sql, book_id)
        res = self.cursor.fetchone()

        if res:
            print("\n========== 书籍详情 ==========")
            print(f"书籍编号：{res['book_id']}")
            print(f"书名：{res['book_name']}")
            print(f"作者：{res['name']}")
            print(f"分类：{res['major']}")
            print(f"状态：{res['state']}")
            self.write_log(f"查询书籍数据：图书编号{book_id}")
        else:
            print("❌ 未查询到该书籍信息！")
            self.write_log(f"查询书籍数据：图书编号{book_id} 未查询到")
            return

    # 更新书籍信息
    def update_book(self, book_id, book_name, name,major):
        sql = """
        UPDATE book
        SET book_name = %s, name = %s, major = %s
        WHERE book_id = %s
        """
        self.cursor.execute(sql, (book_name, name,major, book_id))
        self.conn.commit()
        print("图书信息更新成功")
        self.write_log(f"更新书籍数据：图书编号{book_id} {book_name} {name} {major}")
    
    
    # 删除书籍信息
    def delete_book(self, book_id):
        print('1.删除')
        print('2.取消')
        i=int(input('请输入您的选择：1/2'))
        if i==1:
            try:
                sql = "DELETE FROM book WHERE book_id=%s"
                self.cursor.execute(sql, book_id)
                self.conn.commit()

                if self.cursor.rowcount > 0:
                  print("书籍信息已全部删除")
                  self.write_log(f"删除书籍数据：图书编号{book_id}")
                else:
                     print("未找到该书籍")
            except Exception as e:
               self.conn.rollback()
               print(f"删除失败：{e}")
        elif i==2:
            print(" 操作取消")
            self.write_log(f"删除书籍数据：图书编号{book_id} 操作取消")
        else:
         print('请输入1或2')
    
    # 登录方法
    def login(self, username, password):
        sql = "SELECT role FROM admin WHERE username=%s AND password=%s"
        self.cursor.execute(sql, (username, password))
        result = self.cursor.fetchone()
        if result:
            return result['role']

        return None
    
    # 添加用户账号
    def add_account(self):
        username = input("请输入用户名：")
        password = input("请输入密码：")
        role = input("请输入角色(admin/student)：")
        
        if role not in ['admin', 'student']:
            print("角色只能是 admin 或 student")
            return
        
        try:
            sql = "INSERT INTO admin(username, password, role) VALUES(%s, %s, %s)"
            self.cursor.execute(sql, (username, password, role))
            self.conn.commit()
            print("账号添加成功")
            self.write_log(f"添加账号：{username} ({role})")
        except Exception as e:
            self.conn.rollback()
            print(f"添加失败：{e}")
            self.write_log(f"添加失败：{e}")
    
    # 关闭连接
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    # 查看状态
    def ktate(self,book_id):
        sql = "SELECT state FROM book WHERE book_id=%s"
        self.cursor.execute(sql, (book_id,))
        result = self.cursor.fetchone()
        if result:
            return result['state']
        return None
    # 图书借阅
    def jiey(self, book_id,state):
        
        role=self.ktate(book_id)
        if role == '可借阅':
           sql = """
            UPDATE book
            SET state = %s
            WHERE book_id = %s
            """
           self.cursor.execute(sql, ('已借出', book_id))
           self.conn.commit()
           self.write_log(f"借阅图书：{book_id} 已借出")
        elif role == '已借出':
            print("不可借阅")
            self.write_log(f"借阅图书：{book_id} 不可借阅")
        print("图书信息更新成功")
    #  图书归还
    def guihuan(self, book_id):
        role=self.ktate(book_id)
        if role == '已借出':
           sql = """
            UPDATE book
            SET state = %s
            WHERE book_id = %s
            """
           self.cursor.execute(sql, ('可借阅', book_id))
           self.conn.commit()
           self.write_log(f"归还图书：{book_id} 已归还")
        elif role == '可借阅':
            print("已经归还")

        print("图书信息更新成功")

def admin_menu(sm):

    while True:
        print("\n======= 图书管理系统【管理员版】=======")
        print("1. 添加书籍")
        print("2. 查看所有图书完整信息")
        print("3. 按书籍编号查询书籍信息")
        print("4. 修改图书基础信息")
        print("5. 删除书籍")
        print("6. 查看所有操作日志")
        print("7. 添加账号")
        print('8.图书借阅')
        print('9.图书归还')
        print("0. 退出系统")
        print("==============================================")

        choice = input("请输入功能编号：")

        if choice == "1":
            book_id = input("请输入书籍编号：")
            book_name = input("请输入书名：")
            name = input("请输入作者：")
            major = input("请输入分类：")
            sm.add_book(book_id, book_name, name, major)

        elif choice == "2":
            sm.show_all_book()

        elif choice == "3":
            book_id = input("请输入查询书籍编号：")
            sm.search_id(book_id)

        elif choice == "4":
            book_id = input("请输入要修改的书籍编号：")
            book_name = input("请输入新书名：")
            name = input("请输入新作者：")
            major = input("请输入新分类：")
            sm.update_book(book_id, book_name, name, major)

        elif choice == "5":
            book_id = input("请输入要删除的书籍编号：")
            sm.delete_book(book_id)

        elif choice == "6":
            sm.show_all_logs()

        elif choice == "7":
            sm.add_account()

        elif choice =='8':
            sm.jiey()

        elif choice =='9':
            sm.guihuan()

        elif choice == "0":
            sm.close()
            print("系统退出成功，再见！")
            break

        else:
            print("输入无效，请输入0-7的数字！")


def student_menu(sm):
    while True:
        print("\n======= 图书管理系统【学生版】=======")
        print("1. 查看所有图书")
        print("2. 按编号查询书籍")
        print('3.图书借阅')
        print('4.图书归还')
        print("0. 退出系统")
        print("==============================================")

        choice = input("请输入功能编号：")

        if choice == "1":
            sm.show_all_book()

        elif choice == "2":
            book_id = input("请输入查询书籍编号：")
            sm.search_id(book_id)
        elif choice == "3":
            book_id = input("请输入要借阅的书籍编号：")
            sm.jiey(book_id,'已借出')
        elif choice == "4":
            book_id = input("请输入要归还的书籍编号：")
            sm.guihuan(book_id)
        elif choice == "0":
            sm.close()
            print("系统退出成功，再见！")
            break

        else:
            print("输入无效，请输入0-4的数字！")
def main():
    sm = bookManager()

    # 登录循环
    while True:
        print("\n======= 图书管理系统登录 =======")
        username = input("用户名：")
        password = input("密码：")
        role = sm.login(username, password)

        if role == 'admin':
            print("管理员登录成功")
            sm.write_log(f"管理员登录成功：{username}")
            admin_menu(sm)
            break
        elif role == 'student':
            print("学生登录成功")
            sm.write_log(f"学生登录成功：{username}")
            student_menu(sm)
            break
        else:
            print("用户名或密码错误，请重新登录")


if __name__ == "__main__":
    main()   