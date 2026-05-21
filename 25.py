class Attributes:
    def __init__(self, account_id, name, __balance, __password):
        self.account_id = account_id
        self.name = name
        self.__balance = __balance
        self.__password = __password
    
    # 查看余额（需要密码）
    def get_balance(self):
        a = int(input("请输入密码查看余额: "))
        if a == self.__password:
            print(f'当前余额: {self.__balance}')
            return self.__balance
        else:
            print('密码错误')
            return None
    
    # 存款功能（需要密码）
    def deposit(self):
        a = int(input("请输入密码进行存款: "))
        if a == self.__password:
            b = int(input("请输入存款金额: "))
            if b > 0:
                self.__balance = self.__balance + b
                print(f"存款成功！当前余额: {self.__balance}")
                return self.__balance
            else:
                print("存款金额必须大于0")
        else:
            print('密码错误')
            return None
    
    # 取款功能（需要密码）
    def qukuan(self):
        a = int(input("请输入密码进行取款: "))
        if a == self.__password:
            b = int(input("请输入取款金额: "))
            if 0 < b <= self.__balance:
                self.__balance = self.__balance - b
                print(f"取款成功！当前余额: {self.__balance}")
                return self.__balance
            else:
                print("取款金额必须大于0且小于等于余额")
        else:
            print('密码错误')
            return None
    
    # 修改密码功能
    def gaimm(self):
        a = int(input("请输入原密码: "))
        if a == self.__password:
            b = int(input("请输入新密码: "))
            self.__password = b
            print(f"修改密码成功，新密码: {self.__password}")
            return self.__password
        else:
            print('密码错误')
            return None

    def lix(self):
        a = int(input("请输入密码查看利息: "))
        if a == self.__password:
            c=int(input('请输入查看年份：'))
            for i in range(c):
             self.__balance=self.__balance+self.__balance*0.015*i
             print(f'第{c}年余额:{self.__balance}')
        else:
            print('密码错误')
            return None

# 创建账户实例
s1 = Attributes(1, '叶', 110000000000, 123456)

# 操作菜单
while True:
    print('\n===== 账户操作菜单 =====')
    print('1: 查看余额')
    print('2: 存款')
    print('3: 取款')
    print('4: 改密码')
    print('5:查看利息')
    print('6: 退出')
    
    try:
        i = int(input('请输入选项: '))
        
        if i == 1:
            s1.get_balance()
        elif i == 2:
            s1.deposit()
        elif i == 3:
            s1.qukuan()
        elif i == 4:
            s1.gaimm()
        elif i==5:
            s1.lix()
        elif i == 6:
            print("退出系统")
            break
        else:
            print('请输入1~5选项')
    except ValueError:
        print('请输入有效的数字')