num = input("请输入一个三位数: ")
if len(num) == 3 and num.isdigit():
   hundreds = int(num[0])      # 百位（第一个字符）
   tens = int(num[1])          # 十位（第二个字符）
   units = int(num[2])         # 个位（第三个字符）
   print(f"百位: {hundreds}")
   print(f"十位: {tens}")
   print(f"个位: {units}")
else:
    print("输入错误，请输入一个三位整数！")


     