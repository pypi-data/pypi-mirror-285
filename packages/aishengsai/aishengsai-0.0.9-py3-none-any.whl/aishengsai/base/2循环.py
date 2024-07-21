

#   练习案例: 发工资
#   给20名员工发工资,优秀(绩效>90)5000,达标(绩效大于60)3000,不达标不发工资,总工资30000元,列出明细
import random
sum_money = 30000
great_staff = 0
normal_staff = 0
bad_staff = 0
performance = 0
for staff in range(1, 21):
    performance = random.randint(1, 101)
    if sum_money < 1000:
        print("工资不足,无法发工资")
        break
    if performance > 90:
        if sum_money < 5000:
            print("工资不足,无法发工资")
            break
        sum_money -= 5000
        great_staff += 1
        print(f"优秀员工{staff}号,绩效{performance}分,发工资5000元")
    if performance >= 60:
        if sum_money < 3000:
            print("工资不足,无法发工资")
            break
        sum_money -= 3000
        normal_staff += 1
        print(f"达标员工{staff}号,绩效{performance}分,发工资3000元")
    if performance < 60:
        bad_staff += 1
        print(f"不达标员工{staff}号,绩效{performance}分,不发工资")
        continue
print(f"优秀员工{great_staff}人,达标员工{normal_staff}人,不达标员工{bad_staff}人,此时的工资为{sum_money}元")


#   0-100有多少个偶数
count = 0
i = 0
for i in range(101):
    if i % 2 == 0:
        count += 1
print(f"总共有{count}个偶数")
print(f"此时i的值为{i}")
#   手写九九乘法表
i = 1
j = 1
while i < 10:
    while j <= i:
        print(f"{j}*{i}={i*j}", end="\t")
        j += 1
    i += 1
    j = 1
    print()

#   九九乘法表
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{i}*{j}={i*j}", end="\t")
    print()

#   循环猜数字游戏
import random
num = random.randint(1, 10)
print(num)
print("Welcome to the guessing game!")
print("I'm thinking of a number between 1 and 10.")
while True:
    guess = int(input("Guess a number between 1 and 10: "))
    if guess == num:
        print("You guessed it!")
        break
    elif guess > num:
        print("Too high!")
    else:
        print("Too low!")
