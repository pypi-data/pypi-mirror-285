# createBy yyj
# createTime: 2024/6/26 16:20

# # 打开文件
# # file = open("./resources/居民信息.xlsx", 'r', encoding="UTF-8")   # 这种文件用这种方式读取不出东西来
# file = open("./resources/文本文档读取.txt", 'r', encoding="UTF-8")
# print(type(file))
# # 读取文件-read（）
# # 多次读取文件，后面的读取是在上一次的基础上读取的，例如第一次读取了10个字[file.read(10)]，再一次file.read()，则读取的是第11个字到结尾
# # print(file.read(3))
# # print(file.read())
# # 读取文件-readline（）
# lines = file.readlines()
# print(f'file.readlines()读取到的类型是：{type(lines)}')
# print(lines)
#
# for line in lines:
#     print(line)
# # 记得关闭文件
# file.close()

"""
with语句：
    with语句会自动关闭文件，不需要手动关闭
    with语句会自动打开文件，不需要手动打开
"""


file = open("./resources/统计单词出现的个数.txt", 'r', encoding="UTF-8")
contentText = file.read()
print(contentText)

count = 0
with open("./resources/统计单词出现的个数.txt", 'r', encoding="UTF-8") as file:
    for line in file:
        line = line.strip()
        worlds = line.split(' ')
        for world in worlds:
            if world == 'itheima':
                count += 1
    print(f'itheima出现的次数是：{count}')

count1 = 0
with open("./resources/统计单词出现的个数.txt", 'r', encoding="UTF-8") as file:
    content = file.read()
    count1 = content.count('itheima')
    print(f'itheima1出现的次数是：{count1}')


# 写文件
print("----------------------------------------------------------------------------------------------------------------")
# 'w': 覆盖写入

# 单独操作
file = open("./resources/文本文档写入.txt", 'w', encoding="UTF-8")
# 这只是写入到临时缓冲区，需要手动刷新
file.write("你好我是程序写入的内容\n")
#  手动刷新，将内容刷新到硬盘
# file.flush()
# close() 其实内置了 flush() 的方法
file.close()


"""
with语句：
    with语句会自动关闭文件，不需要手动关闭
    with语句会自动打开文件，不需要手动打开
"""
# 追加模式
with open("./resources/文本文档写入.txt", 'a', encoding="UTF-8") as file:
    file.write("itheima1\n")
    file.write("itheima2\n")



print("----------------------------------------------------------------------------------------------------------------")
# 训练，读文件、写文件
fr = open("./resources/bill.txt", 'r', encoding="UTF-8")
fw = open("./resources/bill_copy.txt", 'w', encoding="UTF-8")
for line in fr:
    # line = line.strip()
    if line.split(",")[4] == '测试\n':
        continue
    fw.write(line)
fr.close()
fw.close()
