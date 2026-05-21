a=input("输入一个单词:")  
b=''
for i in a:
    if 'a'<= i<='z':
        b=b+chr(ord(i)-32)
    elif 'A'<= i<='Z':
        b=b+chr(ord(i)+32)
    else:
        b=b+i
print(b)
