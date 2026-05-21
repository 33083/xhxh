a=[1,2,3,4]
b = ['叶', '石', '吴', '王']
c=[50,30,20,10]
d=list(zip(a,b,c))
print(d)

for i in c:
    if c > 60:
       print('及格')
    else:
       print('不及格')

print(list(zip(a,b,c,e)))