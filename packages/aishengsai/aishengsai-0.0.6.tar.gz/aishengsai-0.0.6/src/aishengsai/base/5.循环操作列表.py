# createBy yyj
# createTime: 2024/4/11 9:29

i = 0
list = []

while i < 10:
    list.append(i)
    i += 1
    print(list)

i = 0
evenList = []
while i < len(list):
    if list[i] % 2 == 0:
        evenList.append(list[i])
    i += 1
print(evenList)


for num in list:
    if num % 2 == 0:
        evenList.append(num)
print(evenList)


