# createBy yyj
# createTime: 2024/7/2 10:59

from my_utils import str_util

strResult = str_util.str_reverse("我是中国人")
print(strResult)

strSubResult = str_util.sub_str("我是中国人", 1, 3)
print(strSubResult)


from my_utils import file_util
file_util.print_file_info("test.txt")
file_util.append_to_file("test.txt", "我是中国人")
