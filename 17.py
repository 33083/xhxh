# a=['1','2','3']
# c=['a','b','c']
# b=dict(zip(a,c))
# print(b)
# d=b.items()
# print(d)
# print(b.keys())
# print(b.values())
# f=input()
# print(b.get(f))




# a=['1','2','3']
# b=['叶','王','石']
# c=['男','女','男']
# d=['12','23','34']
# e=dict(zip(a,[{'姓名': f,'性别':g,'联系方式':h} for f,g,h in zip(b,c,d)]))
# print(e)
# a=input()
# if a in e:
#     contact = e[a]["联系方式"]
#     print(f"学号 {a} 的联系方式是：{contact}")
    
#     gender = e[a]["性别"]
#     if gender == "男":
#         print(f"学号 {a} 的学生是男生")
#     elif gender == "女":
#         print(f"学号 {a} 的学生是女生")
# else:
#     print(f"未找到学号为 {target_id} 的学生")

# print("所有学生信息如下：")
# # 遍历外层字典，拿到学号和学生信息
# for i,j  in e.items():
#     # 按题目要求的格式输出，不直接打印字典
#     print(f"学号：{i}  姓名：{j['姓名']}  性别：{j['性别']}  联系方式：{j['联系方式']}")
# s = input("请输入学号：")
# k= input("请输入姓名：")
# l= input("请输入性别：")
# m= input("请输入联系方式：")
# e[s] = {'姓名': k, '性别': l, '联系方式': m}
# print(e)
# n=input("删除：")
# del e[n]
# print(e)
# o=input()
# p=input()
# q=input()
# e[o][p] =q
# print(e)

# s = input("请输入要筛选的性别（男/女）：")
# result = {sid: info for sid, info in e.items() if info['性别'] == s}
# print(result)

# 初始化数据
a = ['1', '2', '3']
b = ['叶', '王', '石']
c = ['男', '女', '男']
d = ['12', '23', '34']

e = dict(zip(a, [{'姓名': f, '性别': g, '联系方式': h} for f, g, h in zip(b, c, d)]))

def show():
    """显示所有学生信息"""
    if not e:
        print("暂无学生数据。")
        return
    print("\n所有学生信息如下：")
    for sid, info in e.items():
        print(f"学号：{sid}  姓名：{info['姓名']}  性别：{info['性别']}  联系方式：{info['联系方式']}")
    print()

def query():
    """根据学号查询学生信息"""
    sid = input("请输入要查询的学号：")
    if sid in e:
        info = e[sid]
        print(f"学号 {sid} 的姓名：{info['姓名']}，性别：{info['性别']}，联系方式：{info['联系方式']}")
    else:
        print(f"未找到学号为 {sid} 的学生")

def add_student():
    """添加新学生"""
    sid = input("请输入学号：")
    if sid in e:
        print("学号已存在，如需修改请使用修改功能。")
        return
    name = input("请输入姓名：")
    gender = input("请输入性别（男/女）：")
    phone = input("请输入联系方式：")
    e[sid] = {'姓名': name, '性别': gender, '联系方式': phone}
    print(e)
    print("添加成功！")

def delete():
    """删除学生"""
    sid = input("请输入要删除的学号：")
    if sid in e:
        del e[sid]
        print("删除成功！")
    else:
        print("学号不存在。")

def update():
    """修改学生的某个字段"""
    sid = input("请输入要修改的学号：")
    if sid not in e:
        print("学号不存在。")
        return
    field = input("请输入要修改的字段（姓名/性别/联系方式）：")
    if field not in e[sid]:
        print("字段名错误，只能修改姓名、性别或联系方式。")
        return
    new_value = input(f"请输入新的{field}：")
    e[sid][field] = new_value
    print("修改成功！")

def filter_by_gender():
    """按性别筛选学生"""
    gender = input("请输入要筛选的性别（男/女）：")
    result = {sid: info for sid, info in e.items() if info['性别'] == gender}
    if not result:
        print("没有找到该性别的学生。")
        return
    print(f"\n性别为【{gender}】的学生如下：")
    for sid, info in result.items():
        print(f"学号：{sid}  姓名：{info['姓名']}  联系方式：{info['联系方式']}")
    print()

def main():
    """主菜单循环"""
    while True:
        print("\n===== 学生信息管理系统 =====")
        print("1. 显示所有学生")
        print("2. 查询学生（按学号）")
        print("3. 添加学生")
        print("4. 删除学生")
        print("5. 修改学生信息")
        print("6. 按性别筛选")
        print("0. 退出系统")
        choice = input("请输入选项（0-6）：")

        if choice == '1':
            show()
        elif choice == '2':
            query()
        elif choice == '3':
            add()
        elif choice == '4':
            delete()
        elif choice == '5':
            update()
        elif choice == '6':
            filter_by_gender()
        elif choice == '0':
            print("感谢使用，再见！")
            break
        else:
            print("无效选项，请重新输入。")

if __name__ == "__main__":
    main()