a = input("请输入直角三角形的直角边的长度: ")
b = input("请输入直角三角形的另一个直角边的长度: ")

# 先检查是否为数字，再转换并比较
if a.isdigit() and b.isdigit():
    a_num = float(a)
    b_num = float(b)
    if a_num > 0 and b_num > 0:
        c = (a_num**2 + b_num**2)**0.5
        print(f"直角三角形的斜边长度为: {c}")
    else:
        print("输入错误，请输入两个大于0的数！")
else:
    print("输入错误，请输入有效的数字！")
