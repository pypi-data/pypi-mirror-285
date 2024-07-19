from typing import Dict, Union

import fastapi
import requests
from requests import Response

# 存储系统的基本URL，用于所有HTTP请求
option = {"baseUrl": "http://localhost:10001"}


def __check_res__(
    res: Response,
    status_code_mapper: Union[Dict[int, int], None] = None,
    check: bool = True,
):
    """
    根据响应对象检查HTTP请求的响应状态码。

    如果设置了status_code_mapper，则会根据映射关系返回相应的状态码；
    如果响应体是JSON格式，则将详细信息设为解析后的JSON对象；
    如果响应体是其他格式，则将详细信息设为响应体的文本内容。

    参数:
    - res: Response对象，包含HTTP请求的响应信息。
    - status_code_mapper: 字典类型，用于映射HTTP状态码。默认为None。
    - check: 布尔类型，决定是否进行状态码检查。默认为True。

    返回:
    - Response对象，未经修改的响应对象。

    异常:
    - HTTPException: 如果状态码不在200-299范围内，且check为True，则抛出HTTPException异常。
    """
    # 当检查开启时，才进行状态码的检查
    if check:
        # 如果状态码不在200-299范围内
        if res.status_code >= 300 or res.status_code < 200:
            detail = None
            # 如果响应头指示内容类型为JSON，则尝试解析响应体为JSON
            if res.headers.get("Content-Type") == "application/json":
                detail = res.json()
            # 如果响应体不为空，则将响应体文本作为详细信息
            elif res.text:
                detail = res.text
            # 如果提供了状态码映射，则使用映射状态码，否则使用原状态码
            if status_code_mapper is None:
                status_code_mapper = {}
            raise fastapi.HTTPException(
                status_code=status_code_mapper.get(res.status_code, res.status_code),
                detail=detail,
            )
    # 返回原响应对象
    return res


def save(data: dict, status_code_mapper: Dict[int, int] = None, check: bool = True):
    """
    保存数据到存储系统。

    :param status_code_mapper: 异常状态码映射表
    :param check: 是否要检查请求是否成功
    :param data: 需要保存的数据字典。
    :return: HTTP请求的响应。
    """
    if status_code_mapper is None:
        status_code_mapper = {}
    return __check_res__(
        requests.post(option["baseUrl"] + "/storage/save", json=data),
        status_code_mapper,
        check,
    )


def search(data: dict, status_code_mapper: Dict[int, int] = None, check: bool = True):
    """
    根据条件搜索数据。

    :param status_code_mapper: 异常状态码映射表
    :param check: 是否要检查请求是否成功
    :param data: 包含搜索条件的字典。
    :return: HTTP请求的响应。
    """
    return __check_res__(
        requests.post(option["baseUrl"] + "/storage/search", json=data),
        status_code_mapper,
        check,
    )


def get(params: dict, status_code_mapper: Dict[int, int] = None, check: bool = True):
    """
    获取特定资源。

    :param status_code_mapper: 异常状态码映射表
    :param check: 是否要检查请求是否成功
    :param params: 包含查询参数的字典。
    :return: HTTP请求的响应。
    """
    return __check_res__(
        requests.get(option["baseUrl"] + "/storage/get", params=params),
        status_code_mapper,
        check,
    )


def delete(data: dict, status_code_mapper: Dict[int, int] = None, check: bool = True):
    """
    删除指定的数据。

    :param status_code_mapper: 异常状态码映射表
    :param check: 是否要检查请求是否成功
    :param data: 包含删除条件的字典。
    :return: HTTP请求的响应。
    """
    return __check_res__(
        requests.post(option["baseUrl"] + "/storage/delete", json=data),
        status_code_mapper,
        check,
    )


def set_default_collection_type(
    _type: str, status_code_mapper: Dict[int, int] = None, check: bool = True
):
    """
    设置默认的集合类型。

    :param status_code_mapper: 异常状态码映射表
    :param check: 是否要检查请求是否成功
    :param _type: 新的默认集合类型。
    :return: HTTP请求的响应。
    """
    return __check_res__(
        requests.post(
            option["baseUrl"] + "/storage/collection/default", params={"type": _type}
        ),
        status_code_mapper,
        check,
    )
