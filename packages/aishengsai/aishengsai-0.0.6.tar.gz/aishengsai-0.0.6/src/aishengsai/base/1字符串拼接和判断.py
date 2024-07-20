
#   拼接
print("Hello World" + "2")

print("Hello World %s ,%s" %("1",2))

sum = 1 + 2
print(f"Hello World {1} ,{2}, {sum}")



#   输入和判断
age = input("欢迎来到儿童乐园,儿童免费,成人10元."
"请输入你的年龄:")
age = int(age)
if age >= 18:
    print("请支付10元")
elif age >= 10:
    print("请支付1元")
else:
    print("免费")


if int(input("请输入你的身高：")) > 120:
    if int(input("请输入你的VIP级别：")) > 3:
        print("可以免费游玩")
    else:
        print("请支付100元")
else:
    print("欢迎你小朋友")
