from fastapi import FastAPI
from pydantic import BaseModel
import pymysql
from typing import List

# 创建 FastAPI 应用实例
app = FastAPI(title="学生管理系统", description="基于 FastAPI 的学生信息管理接口")

def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='student_db',
        charset='utf8mb4',
        port=3307,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

class Student(BaseModel):
    id: int
    name: str
    age: int

class StudentList(BaseModel):
    students: List[Student]

# @app.get("/students", summary="获取所有学生信息")
# def get_all_students():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM students")
#     students = cursor.fetchall()
#     conn.close()
#     return {"data": students}
@app.get("/students/{name}")
def get_student(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM students WHERE name like %s", (f"%{name}%",))
    student = cursor.fetchone()
    conn.close()
    return {"data": student}


@app.post("/students/")
def create_student(stu: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO students (id, name, age) VALUES (%s, %s, %s)", (stu.id, stu.name, stu.age))
    conn.commit()
    conn.close()            
    return {"data": "创建成功"}

@app.put("/students/{id}")
def update_student(id: int, stu: Student):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE students SET name = %s, age = %s WHERE id = %s", (stu.name, stu.age, id))
    conn.commit()
    conn.close()
    return {"data": "更新成功"}

@app.delete("/students/{id}")
def delete_student(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return {"data": "删除成功"}


@app.get("/students", summary="获取学生总数和平均年龄")
def get_student_stats():
    import traceback
    try:
        print("=== 进入统计接口 ===")
        conn = get_db_connection()
        print("数据库连接成功")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total, AVG(CAST(age AS UNSIGNED)) AS avg_age FROM students")
        result = cursor.fetchone()
        print("查询结果:", result)
        conn.close()
        
        if result and result.get('total', 0) > 0:
            total = result['total']
            avg_age = float(result['avg_age']) if result.get('avg_age') is not None else 0.0
            return {"data": {"total_students": total, "average_age": avg_age}}
        else:
            return {"data": {"total_students": 0, "average_age": 0}}
    except Exception as e:
        print("发生异常:")
        traceback.print_exc()
        return {"error": str(e), "trace": traceback.format_exc()}


@app.post("/students/batch", summary="批量插入学生信息")
def create_students_batch(stu_list: StudentList):
    conn = get_db_connection()
    cursor = conn.cursor()
    inserted_count = 0
    errors = []
    
    try:
        # 准备批量插入的 SQL（使用 executemany）
        sql = "INSERT INTO students (id, name, age) VALUES (%s, %s, %s)"
        data = [(stu.id, stu.name, stu.age) for stu in stu_list.students]
        
        # 执行批量插入
        cursor.executemany(sql, data)
        conn.commit()
        inserted_count = cursor.rowcount  # 成功插入的行数
        
        return {
            "code": 200,
            "message": f"批量插入成功，共插入 {inserted_count} 条记录",
            "data": {
                "inserted_count": inserted_count,
                "students": stu_list.students
            }
        }
    except pymysql.IntegrityError as e:
        # 处理主键重复等完整性错误
        conn.rollback()
        return {
            "code": 400,
            "message": f"数据完整性错误: {e.args[1]}",
            "data": None
        }
    except Exception as e:
        conn.rollback()
        return {
            "code": 500,
            "message": f"批量插入失败: {str(e)}",
            "data": None
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("y:app", host="0.0.0.0", port=8000, reload=True)