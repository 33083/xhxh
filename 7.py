a=['苹果','香蕉','橘子']
for index,value in enumerate(a,start=1):
    print(index,value)


a=['苹果','香蕉','橘子']
def find(x):
    for index,value in enumerate(a,start=1):
        if value == x:
            print(f"{x}的下标:{index}")
            break
        else:
            print(f'列表里没有该元素')
            break
    
            
find('苹果')
find('榴莲')

