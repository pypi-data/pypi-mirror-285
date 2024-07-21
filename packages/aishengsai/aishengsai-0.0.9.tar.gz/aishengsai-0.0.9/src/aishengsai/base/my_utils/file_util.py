# createBy yyj
# createTime: 2024/7/2 10:56

def print_file_info(file_path):
    """
    打印文件信息
    :param file_path: 文件路径
    :return:
    """
    f = None
    try:
        f = open(file_path, 'r', encoding='utf-8')
        print(f'文件名: {f.name}')
        print(f'文件内容：{f.read()}')
    except FileNotFoundError:
        print(f'文件{file_path}不存在')
        return
    finally:
        if f:
            f.close()
            print(f'文件{file_path}已关闭')

def append_to_file(file_path, data):
    """
    追加内容到文件
    :param file_path: 文件路径
    :param data: 要追加的内容
    :return:
    """
    f = None
    try:
        f = open(file_path, 'a', encoding='utf-8')
        f.write(data)
        print(f'文件{file_path}已追加内容')
    except FileNotFoundError:
        print(f'文件{file_path}不存在')
        return
    finally:
        if f:
            f.close()
            print(f'文件{file_path}已关闭')
