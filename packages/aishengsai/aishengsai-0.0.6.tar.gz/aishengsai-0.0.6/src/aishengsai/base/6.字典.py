# createBy yyj
# createTime: 2024/4/11 17:59

employ_info = {
    "王力宏": {
        "部门": "科技部",
        "级别": 1,
        "工资": 2000
    },
    "周润发": {
        "部门": "影视部",
        "级别": 3,
        "工资": 3000
            }
}

print(f"升职加薪前{employ_info}")
# 升职加薪
# 这个for取到的是他的key

for key in employ_info:
    if employ_info[key]["级别"] == 1:
        employ_info[key]["级别"] += 1
        employ_info[key]["工资"] += 1000
print(f"升职加薪后{employ_info}")

