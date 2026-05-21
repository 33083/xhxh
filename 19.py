# a="acxsdfdsacvzxawf"
# print(a.find('d'))
# print(a.rfind('d'))
# print(a.index('a'))
# print(a.rindex('a'))
# print(a.count('a'))


str = '叶坚上场了，叶坚使用了她最拿手的英雄，妲己，叶坚直接二技能起手，叶坚被控住了，叶坚没了，叶坚复活了'

for i,j in enumerate(str):
    if i == str.index('叶'):
        print((i,j))
    times = str.count('叶坚')
    print(times)
    break

for i in str:
    a = str.split("，")
    print(a)

    # b = str.rsplit('')
    # print(b)

    c = str.partition('坚')
    print(c)

    d = str.rpartition('坚')
    print(d)
    break



# str = '叶坚上场了，叶坚使用了她最拿手的英雄，妲己，叶坚直接二技能起手，叶坚被控住了，叶坚没了，叶坚复活了'

# a = '叶坚上场了，叶坚使用了她最拿手的英雄'
# # str = str.replace('叶','王')
# # print(str)


# table = a.maketrans('叶坚','王林')
# print(str.translate(table))

