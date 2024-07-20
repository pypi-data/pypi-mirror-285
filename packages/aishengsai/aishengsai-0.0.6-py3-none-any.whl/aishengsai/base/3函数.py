
totalMoney = 50000
name = input("请输入姓名：")


def main():
    print(f"欢迎{name}使用ATM系统")
    print("1.存钱")
    print("2.取钱")
    print("3.查询余额")
    print("4.退出")

def save(money):
    global totalMoney
    totalMoney += money
    print(f"你好,{name},存钱成功，余额为：", totalMoney)

def get(money):
    global totalMoney
    if totalMoney >= money:
        totalMoney -= money
        print(f"你好,{name},取钱成功，余额为：", totalMoney)
    else:
        print("余额不足")

def query():
    print(f"你好,{name},余额为：", totalMoney)


while True:

    main()
    choice = input("请选择：")
    if choice == "1":
        save(int(input("请输入存钱金额：")))
    elif choice == "2":
        get(int(input("请输入取钱金额：")))
    elif choice == "3":
        query()
    elif choice == "4":
        print("谢谢使用")
        break

