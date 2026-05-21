a=input("请输入第一个单词: ")
b=input("请输入第二个单词: ")
c=input("请输入第三个单词: ")

if a>b:
    a,b=b,a
if a>c:
    a,c=c,a
if b>c:
    b,c=c,b
print(a,b,c)

 
