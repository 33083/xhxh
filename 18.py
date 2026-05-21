def demo(a,b=[]):
    b.append(a)
    return b
print(demo('5',[1,2,3,4]))
print(demo('aaa',['a','b']))
print(demo('a'))
print(demo('b'))