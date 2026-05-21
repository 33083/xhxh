a=float(input('请输入成绩：'))
if 90<=a<=100:
    print('该同学成绩为:A')
elif  80<=a<90:
      print('该同学成绩:B')
elif  70<=a<80:
      print('该同学成绩为:C')
elif  60<=a<70:
      print('该同学成绩为:D')
elif  0<=a<60:
      print('该同学成绩:E')
else:
    print('输入错误，请输入0~100的数字')