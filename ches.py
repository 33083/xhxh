test='hello world! I like python. this is a nice day. right'
def lower():
  print(test.lower())

def upper():
  print(test.upper())

# def zc():
#   c=test.split()
#   print(c)
#   print(len(c))
#   d=[]
#   for i in c:
#     if i<= 'world!':
#         a=i.upper()
#         d.append(a)
#     else:
#         b=i.title()
#         d.append(b)
# print(''.join(d))

def new():
  k=int(input())

  lower_letter='abcdefghijklmnopgrstuvwxyz'
  upper_letter='ABCDEFGHIJKLMNOPQRSTUVWXYZ'

  lower_letter_k=lower_letter[k:]+lower_letter[:k]
  upper_letter_k=upper_letter[k:]+upper_letter[:k]

  trans_table = str.maketrans(lower_letter+upper_letter, lower_letter_k+upper_letter_k)

  print(len(lower_letter+upper_letter))
  print(len(lower_letter_k+upper_letter_k))
  new_s = test.translate(trans_table)
  print(new_s)   
def main():
    while True:
        print('单词系统')
        print('1:全部大写')
        print('2:全部小写')
        print('3:转换成正确格式')
        print('4:加密操作')
        print('5:退出操作')
        f=int(input())
        if f == 1:
            lower()
        elif f == 2:
            upper()
        elif f==3:
            zc()
        elif f==4:
            new()
        elif f==5:
            break
        else:
         print('请输入1~5选项')

         





