import requests

# 存储系统的基本URL，用于所有HTTP请求
option = {"baseUrl": "http://localhost:10001"}


def save(data: dict):
    """
    保存数据到存储系统。

    :param data: 需要保存的数据字典。
    :return: HTTP请求的响应。
    """
    return requests.post(option["baseUrl"] + "/storage/save", json=data)


def search(data: dict):
    """
    根据条件搜索数据。

    :param data: 包含搜索条件的字典。
    :return: HTTP请求的响应。
    """
    return requests.post(option["baseUrl"] + "/storage/search", json=data)


def get(params: dict):
    """
    获取特定资源。

    :param params: 包含查询参数的字典。
    :return: HTTP请求的响应。
    """
    return requests.get(option["baseUrl"] + "/storage/get", params=params)


def delete(data: dict):
    """
    删除指定的数据。

    :param data: 包含删除条件的字典。
    :return: HTTP请求的响应。
    """
    return requests.post(option["baseUrl"] + "/storage/delete", json=data)


def set_default_collection_type(_type: str):
    """
    设置默认的集合类型。

    :param _type: 新的默认集合类型。
    :return: HTTP请求的响应。
    """
    return requests.post(
        option["baseUrl"] + "/storage/collection/default", params={"type": _type}
    )
