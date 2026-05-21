a=['叶','王','吴','石']
b=[60,70,80,94]
c=[70,80,93,90]
d=[91,92,60,90]
e=list(zip(a,b,c,d))
f=list(zip(b,c,d))
print(e)
x=0
for i in f:
    sums=sum(i)
    g=sums/3
    if g >= 60 and g <=85:
        print(f'学生姓名：{e[x][0]},平均数：{g:.2f},合格')
    elif g<60:
        print(f'学生姓名：{e[x][0]},平均数：{g:.2f},不合格')
    else:
        print(f'学生姓名：{e[x][0]},平均数：{g:.2f},优秀')
    x+=1
l=max(b)
h=max(c)
j=max(d)
q=b.index(l)
w=c.index(h)
r=d.index(j)
print(f'学生姓名：{e[q][0]}语文最高分：{l}')
print(f'学生姓名：{e[w][0]}数学最高分: {h}')
print(f'学生姓名：{e[r][0]}英语最高分: {j}')
