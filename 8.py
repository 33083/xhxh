
a=list(range(11))
def m(x):
      if x%2==1:
       return x

filter(m,a)
list(filter(m,a))
print(list(filter(m,a)))

mi = filter(lambda a:a>0,a)
b=map(lambda a:a*2,mi)
print(list(b))
