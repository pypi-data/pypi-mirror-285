"""
依赖：
    jsonpath_ng==1.6.1
"""
from jsonpath_ng import jsonpath, parse


def json_path_extr(json_path: str, json_data: object) -> object:
    """
    使用 json path 提取数据
    :param json_path: 语法可参考 https://pypi.org/project/jsonpath-ng/
    :param json_data: json 数据，从该数据中提取
    :return: 返回的类型，和你传入的 json_data 中的一致
    """
    docs = parse(json_path).find(json_data)
    if docs:
        return docs[0].value
    return None
