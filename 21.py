# a='abcabcdefghijklmnopgrstuvwxyz'
# print(a.strip('abcd'))
# print(a.strip('yz'))

# test='''姓名    : 张三
# 年龄   :39
# 性别男
# 职业  学生
# 籍贯:    地球'''
# a=test.split('\n')
# print(a)
# for i in a:
#     print(i[:2],i[2:].strip(':   '),sep=': ')

# import string
# print(string.digits)
# print(string.punctuation)
# print(string.ascii_lowercase)
# print(string.ascii_letters)
# print(string.ascii_uppercase)

# import string
# a=string.punctuation
# b=string.digits + string.ascii_letters
# import random
# c=''.join([random.choice(b) for i in range(8)])
# d=''.join([random.choice(a)])
# print(d+c)
  
# s = '''jskskxk \nkkkk\ns2xsxszxscdsfe'''
# with open('sample.txt','w') as fp:
#     fp.write(s)
# with open('sample.txt') as fp:
#     print(fp.read())
# with open('sample.txt','r') as fp:
#     print(fp.read(5))

# with open('sample.txt') as fp:
#     for i in fp:
#       print(i,end='')
# s='''5
# 6
# 7
# 2356
# 5466
# 35436
# 46
# 4'''
# with open('sample.txt','w') as fp:
#     fp.write(s)
#     print(s)
# q=[]
# with open('sample.txt') as fp:
#     for i in fp:
#       i=i.strip()
#       q.append(int(i))
# print(q)
# e=sorted(q)
# with open('sample.txt','w') as fp:
#      for i in e:
#        fp.write(str(i)+'\n')
# import os 

# print(os.getcwd())
# print(os.listdir(os.getcwd()))
# t=os.listdir(os.getcwd())
# for i in t: 
#     if i.endswith('.py') and os.path.isfile:
#         print(i)

# import os
# totalSize,fileNum,dirNum=0,0,0

# def visitDir(path):
#     global totalSize
#     global fileNum
#     global dirNum
#     for lists in os.listdir(path):
#         sub_path=os.path.join(path,lists)
#         if os.path.isfile(sub_path):
#             fileNum=fileNum+1
#             totalSize=totalSize+os.path.getsize(sub_path)
#         elif os.path.isdir(sub_path):
#             dirNum=dirNum+1
#             visitDir(sub_path)
# print(fileNum)
# print(totalSize)

# class ShortInputException(Exception):
#     def __init__(self,length,atleast):
#         Exception.__init__(self)
#         self.length=length
#         self.atleast=atleast
# try:
#     s=input('请输入--> ')
#     if len(s)<3:
#         raise ShortInputException(len(s),3)
# except EOFError:
#     print('结束')
# except ShortInputException as x:
#     print(f'ShortInputException: 长度是{x.length},至少是{x.atleast}' )
# else:
#     print('没有异常')
# c=[]
# while True:
#     x=input()
#     try:
#         x=int(x)
#         c.append(x)
#         continue

#     except Exception as e:
#         print('Error.')
#         break
# print(c)



# c=[]
# while True:
#     x=input()
#     if x=="q":
#         break
#     if x=="":
#         print('错误')
#         continue
#     try:
#         x=int(x)
#         if 0<=x<=100:
#          c.append(x)
#         else:
#          raise ValueError()
#     except ValueError as e:
#         print('请输出正确格式')

# print(c)
def time():
    from datetime import datetime
    now=datetime.now()
    print(now.strftime('%Y-%m-%d %H:%M;%S'))
    print(now.strftime('%A,%B %d,%Y'))

