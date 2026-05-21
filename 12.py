b='yes'
x=0
sum=0
while b=='yes':
   c=float(input('请输入一个数字:'))
   sum+=c
   x+=1
   b=input('是否继续输入:"yes/no":')
d=sum/x
    
print(f'平均数为：{d:.2f}')
print('结束')
if b!='yes' and b!='no':
    print('输入错误')