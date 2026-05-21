a = []
for num in range(101):
    if num <= 1:
        continue
    if num == 2:
        a.append(num)
        continue
    if num % 2 == 0:
        continue
    is_prime = True
    # 检查奇数因子
    for d in range(3, int(num**0.5) + 1, 2):
        if num % d == 0:
            is_prime = False
            break
    if is_prime:
        a.append(num)
b=max(a)
print(b)