import json
import os
from typing import Any


def read_json_data(file_path: str, empty_init_json_obj={}) -> Any:
    """
    读取 json 文件, 并返回 json 对象
    :param file_path: 文件路径
    :param empty_init_json_obj: 当文件不存在时,创建的文件初始内容，同时当成文件内容返回返
    :return:
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(empty_init_json_obj, f)
            return empty_init_json_obj
    with open(file_path, 'r', encoding="utf-8") as f:
        json_data = json.load(f)
        return json_data


def write_json_data(file_path: str, json_data):
    """
    将 json 对象写入文件，该方法会覆盖文件的所有内容
    :param file_path: 文件路径
    :param json_data: json 对象
    :return:
    """
    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False)


def write_line_data(file_path: str, line_data):
    """
    将一行数据写入文件，该方法会在文件末尾追加内容
    :param file_path: 文件路径
    :param line_data: 一行数据
    :return:
    """
    with open(file_path, 'a', encoding="utf-8") as f:
        f.write(line_data + "\n")


def create_dir_if_not_exists(dir_path):
    """
    创建目录，如果目录不存在
    :param dir_path: 目录路径
    :return:
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def read_last_line(file_path):
    """
    读取文件最后一行
    :param file_path:
    :return:
    """
    if os.stat(file_path).st_size == 0:
        # 文件为空
        return None
    with open(file_path, "rb") as file:
        # os.SEEK_END 表示从文件末尾开始，第一个参数是偏移量
        # 意思就是，从文件末尾开始读取 2 个字节
        # 这里相当于，指针跳转到了文件末尾的前两个字节
        # 会返回当前的指针位置，另外 file.tell() 也可以得到当前指针位置
        cur_index = file.seek(-2, os.SEEK_END)
        # 然后，每次读取一个字节检查是否是换行符
        while file.read(1) != b'\n':
            # os.SEEK_CUR 表示从当前位置，上面已经读取了 2 个字节
            cur_index = file.seek(-2, os.SEEK_CUR)
            if cur_index == 0:
                # 已经到了文件的开头
                break
        return file.readline().decode()
