# createBy yyj
# createTime: 2024/7/2 9:40

# 异常的捕获
# 捕获所有异常
try:
    f = open("./resources/异常捕获.txt", "r", encoding="UTF-8")
except Exception as e:
    print("出现异常了")
    f = open("./resources/异常捕获.txt", "w", encoding="UTF-8")
else:
    print("好高兴，没有异常。")
finally:
    print("我是finally，有没有异常我都要执行")
    f.close()

"""
演示异常的传递性
"""

# 定义一个出现异常的方法
def func1():
    print("func1 开始执行")
    num = 1 / 0     # 肯定有异常，除以0的异常
    print("func1 结束执行")
# 定义一个无异常的方法，调用上面的方法

def func2():
    print("func2 开始执行")
    func1()
    print("func2 结束执行")
# 定义一个方法，调用上面的方法

def main():
    try:
        func2()
    except Exception as e:
        print(f"出现异常了，异常的信息是：{e}")

main()


# ----------------------------------------------------------------------------------
# 模块和包的引用
# 导入不同模块的同名功能
from my_package.my_module1 import test
from my_package.my_module2 import test
test()
# 以上这种方式，方法名一样，实际执行是后面的覆盖前面的，所以，执行结果是my_module2的test()
# 为了避免这种情况，可以添加一个别名
from my_package.my_module1 import test as test1
from my_package.my_module2 import test as test2
test1()
test2()

# 创建一个包
# 导入自定义的包中的模块，并使用
# import my_package.my_module1
# import my_package.my_module2
#
# my_package.my_module1.info_print1()
# my_package.my_module2.info_print2()

# from my_package import my_module1
# from my_package import my_module2
# my_module1.info_print1()
# my_module2.info_print2()

# 通过__all__变量，控制import *
from my_package import *
my_module1.info_print1()
my_module2.info_print2()
