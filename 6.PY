a=int(input("输入一个数:"))
print("1:加")
print("2:减")
print("3:乘")
print("4:除")
c=int(input("输入要求："))
b=int(input("输入另一个数:"))
if c==1:
    print(a+b)
elif c==2:
    print(a-b)
elif c==3:
    print(a*b)
elif c==4:
    if b==0:
        print("除数不能为0！")
    else:
        print(a/b)
else:
    print("输入错误，请输入1-4之间的整数！")
print("是否继续运算")
d=input("1:是 2:否")
if d=='1':
    print("继续运算")
    print("1:加")
    print("2:减")
    print("3:乘")
    print("4:除")
    print 
    c=int(input("输入要求："))
    if c==1:
        print(a+b+e)
    elif c==2:
        print(a-b)
    elif c==3:
        print(a*b)
    elif c==4:
        if b==0:
            print("除数不能为0！")
        else:
            print(a/b)
    else:
        print("输入错误，请输入1-4之间的整数！")
else:
    print("结束运算")