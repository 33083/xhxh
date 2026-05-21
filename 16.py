a=[]
for i in range(3):
    i=input()
    a.append(i)
    print(a)
a.reverse()
print(a)
b=int(input())
print(a.count(a[b]))