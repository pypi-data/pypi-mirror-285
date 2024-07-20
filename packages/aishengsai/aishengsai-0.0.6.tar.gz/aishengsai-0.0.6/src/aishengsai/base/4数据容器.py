
# 列表
list = [1, 2, "gou", 4, 5]
list.append(6)

# 查询
print(list[0])

# 查询 倒着数,最后一个为-1,从右到左减1为倒数第2
print(list[-3])

# 查询 根据元素查找元素所在下标
print(list.index("gou"))

# 插入    指定下标,插入元素
list.insert(0, 1)

# 插入    追加到最后
list.append(9)

# 插入    追加新列表
list1 = [1, 2, 3, 4, 5, "aaa", True]

list.extend(list1)
print(list)

# 删除 删除其中的元素,只删除匹配到的第一个(从左往右)
list.remove(1)
# 删除 删除最后一个元素,并的到最后一个元素即拿到最后一个元素并删除
pop = list.pop()
print(pop)


# 删除 删除指定位置的元素
del list[0]

# 统计元素在列表中的个数
print(f"元素3在列表中的个数为:{list.count(3)}")

# 统计列表中全部元素数量
print(f"列表中全部元素数量为:{len(list)}")

# 列表排序  需要列表内容类型一致
# list.sort()

# 反转
list.reverse()
print(f"列表反转后为:{list}")

# 清空列表
list.clear()

