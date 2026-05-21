# a=[]
# for i in range(1,101):
#     if i%5==0 and i%7!=0:
#         a.append(i)
# print(a)

# a=[]
# for i in range(100,1000):
#     if (i%10)**3+((i//10)%10)**3+(i//100)**3==i:
#         a.append(i)
# print(a)


n=int(input())
for i in range(10**(n-1),10**n):
    if sum(map(lambda i: int(i)**n,str(i)))==i:
        print(i)