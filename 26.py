# import pymysql

# conn = None
# cursor = None

# try:
#     conn = pymysql.connect(
#         host='localhost',
#         user='root',
#         password='123456',
#         database='company',
#         port=3307
#     )
#     print("连接成功")
    
#     # cursor = conn.cursor()
#     # sql = "INSERT INTO employees (name, salary, position, department, entry_date, gender) VALUES (%s, %s, %s, %s, %s, %s)"
#     # data = [('吴', 200, '计师', '设计部', '2021-02-11', '男'),
#     #         ('赖', 200, '计师', '设计部', '2021-02-11', '女')]
    
#     # cursor.executemany(sql, data)
#     # conn.commit()
#     # print(f"成功插入 {cursor.rowcount} 条记录")
#     cursor =conn.cursor()
#     # sql = "INSERT INTO employees (name, salary, position, department, entry_date, gender) VALUES (%s, %s, %s, %s, %s, %s)"
#     # date=('钱九', 18000, '测试工程师', '工程部', '2021-02-11', '男')
#     # cursor.execute(sql, date)
#     # conn.commit()
#     # sql="update employees set  salary =%s where name=%s"
#     # cursor.execute(sql, (20000,'张三'))
#     # conn.commit()
# #     sql='''
# #     CREATE table user (
# #     id INT PRIMARY KEY AUTO_INCREMENT,
# #     username VARCHAR(50) NOT NULL,
# #     password VARCHAR(50) NOT NULL,
# #     phone VARCHAR(20),
# #     gender CHAR(1) COMMENT '性别: M男 F女'
# # );
# # '''
# def a():
# #     sql='''
# # INSERT INTO user (username, password, phone, gender) VALUES
# # ('张三', 'pass123', '13800138001', '男'),
# # ('李四', 'pass456', '13800138002', '男'),
# # ('王芳', 'pass789', '13800138003', '女'),
# # ('赵雷', 'pass000', '13800138004', '男'),
# # ('孙丽', 'pass999', '13800138005', '女');
# # '''
# #     sql='''
# # select *from user where gender=%s
# # '''
# #     cursor.execute(sql,('男'))
# #     conn.commit()
# #     result=cursor.fetchall()
# #     print(result)
# #    
# #     sql='''
# # delete from user where  username=%s
# # '''
# #     cursor.execute(sql,('张三'))
# #     conn.commit()
#     # conn.begin()   # 开始事务
#     # sql_trans1 = '''
#     #     INSERT INTO user (username, password, phone, gender) VALUES ('周杰', 'abc123', '13912345678', 'M')
#     # '''
#     # sql_trans2 = '''
#     #     INSERT INTO user (username, password, phone, gender) VALUES ('林琳', 'def456', '13987654321', 'F')
#     # '''
#     # cursor.execute(sql_trans1)
#     # cursor.execute(sql_trans2)
#     # conn.commit()
#     # print("事务提交成功")
# except pymysql.MySQLError as e:
#     conn.rollback()
#     print(f"操作失败: {e}")
    
# finally:
#     # 先关闭游标
#     if cursor:
#         cursor.close()
#     # 再关闭连接
#     if conn:
#         conn.close()
#     print("资源已释放")
# while True:
#     print("1:插入数据")
#     print("2:查询数据")
#     print("3:删除数据")
#     print("4:更新数据")
#     print("5:退出")
#     choice = int(input("请输入您的选择: "))
#     if choice == 1:
#     elif choice == 2:
#         print("查询数据")
#     elif choice == 3:
#         print("更新数据")
#     elif choice == 4:
#         print("删除数据")
#     elif choice == 5:
#         print("退出")
#         break
#     else:
#         print("无效选择，请重新输入")
import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'company',
    'port': 3307,
    'charset': 'utf8mb4'
}

def get_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def create_table():
    """创建 user 表（如果不存在）"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = '''
        CREATE TABLE IF NOT EXISTS user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(50) NOT NULL,
            phone VARCHAR(20),
            gender CHAR(1) COMMENT 'M:男 F:女'
        )
        '''
        cursor.execute(sql)
        conn.commit()
        print("表 user 已准备就绪")
    except pymysql.MySQLError as e:
        print(f"创建表失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insert_user():
    """插入一条新用户（从控制台输入）"""
    conn = None
    cursor = None
    try:
        print("\n--- 插入新用户 ---")
        username = input("请输入用户名: ").strip()
        password = input("请输入密码: ").strip()
        phone = input("请输入手机号: ").strip()
        gender = input("请输入性别 (M/F): ").strip().upper()
        if gender not in ('M', 'F'):
            print("性别只能是 M 或 F")
            return

        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO user (username, password, phone, gender) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (username, password, phone, gender))
        conn.commit()
        print(f"成功插入 {cursor.rowcount} 条记录，新ID: {cursor.lastrowid}")
    except pymysql.MySQLError as e:
        print(f"插入失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def query_users():
    """查询用户，可按性别过滤，也可以查询所有"""
    conn = None
    cursor = None
    try:
        print("\n--- 查询用户 ---")
        print("1. 查询所有用户")
        print("2. 按性别查询 (M/F)")
        sub = input("请选择: ").strip()
        conn = get_connection()
        cursor = conn.cursor()
        if sub == '1':
            sql = "SELECT id, username, phone, gender FROM user"
            cursor.execute(sql)
        elif sub == '2':
            gender = input("请输入性别 (M/F): ").strip().upper()
            if gender not in ('M', 'F'):
                print("性别无效")
                return
            sql = "SELECT id, username, phone, gender FROM user WHERE gender = %s"
            cursor.execute(sql, (gender,))
        else:
            print("无效选择")
            return

        rows = cursor.fetchall()
        if not rows:
            print("没有找到任何用户")
        else:
            print("\nID\t用户名\t手机号\t\t性别")
            for row in rows:
                print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}")
    except pymysql.MySQLError as e:
        print(f"查询失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_user():
    """更新用户信息（手机号或密码）"""
    conn = None
    cursor = None
    try:
        print("\n--- 更新用户信息 ---")
        uid = input("请输入要更新的用户ID: ").strip()
        if not uid.isdigit():
            print("ID必须是数字")
            return
        uid = int(uid)

        print("1. 更新手机号")
        print("2. 更新密码")
        choice = input("请选择: ").strip()
        if choice == '1':
            new_phone = input("请输入新手机号: ").strip()
            sql = "UPDATE user SET phone = %s WHERE id = %s"
            params = (new_phone, uid)
        elif choice == '2':
            new_pwd = input("请输入新密码: ").strip()
            sql = "UPDATE user SET password = %s WHERE id = %s"
            params = (new_pwd, uid)
        else:
            print("无效选择")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        if cursor.rowcount > 0:
            print(f"成功更新 {cursor.rowcount} 条记录")
        else:
            print("没有找到该ID的用户，更新失败")
    except pymysql.MySQLError as e:
        print(f"更新失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_user():
    """删除用户（根据ID）"""
    conn = None
    cursor = None
    try:
        print("\n--- 删除用户 ---")
        uid = input("请输入要删除的用户ID: ").strip()
        if not uid.isdigit():
            print("ID必须是数字")
            return
        uid = int(uid)
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM user WHERE id = %s"
        cursor.execute(sql, (uid,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"成功删除 {cursor.rowcount} 条记录")
        else:
            print("没有找到该ID的用户")
    except pymysql.MySQLError as e:
        print(f"删除失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """主菜单循环"""
    # 确保表存在
    create_table()

    while True:
        print("\n========== 用户管理系统 ==========")
        print("1. 插入用户")
        print("2. 查询用户")
        print("3. 更新用户")
        print("4. 删除用户")
        print("5. 退出")
        choice = input("请输入您的选择: ").strip()
        if choice == '1':
            insert_user()
        elif choice == '2':
            query_users()
        elif choice == '3':
            update_user()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            print("退出程序")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == '__main__':
    main()