import uuid
from typing import Dict, Union

import bridge
import fastapi
from requests import Response


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


def set_default_collection_type(
    _type: str,
    status_code_mapper: Dict[int, int] = None,
    check: bool = True,
    tid: str = None,
):
    """
    设置默认的集合类型。

    :param tid: 事务id
    :param status_code_mapper: 异常状态码映射表
    :param check: 是否要检查请求是否成功
    :param _type: 新的默认集合类型。
    :return: HTTP请求的响应。
    """
    return __check_res__(
        bridge.post(
            "/storage/collection/default",
            params={"type": _type, "tid": tid},
        ),
        status_code_mapper,
        check,
    )


def transaction_end(
    tid: str,
    rollback: bool = None,
    status_code_mapper: Dict[int, int] = None,
    check: bool = True,
):
    """
    结束指定id的事务。

    :param rollback: 是否回滚事务
    :param tid: 事务id
    :param status_code_mapper: 异常状态码映射表
    :param check: 是否要检查请求是否成功
    :return: HTTP请求的响应。
    """
    return __check_res__(
        bridge.post(
            "/storage/transaction/end",
            params={"tid": tid, "rollback": rollback},
        ),
        status_code_mapper,
        check,
    )


class TransactionContext:
    """
    事务管理类，用于控制事务的开始和结束。

    该类实现了上下文管理器协议，通过`__enter__`和`__exit__`方法控制事务生命周期。
    """

    __id__: str  # 事务唯一标识符

    def __enter__(self):
        """
        当使用`with`语句进入上下文时调用。

        生成并设置一个唯一的事务标识符。
        """
        self.__id__ = str(uuid.uuid4())
        return self

    def __exit__(self, exc_type):
        """
        当使用`with`语句退出上下文时调用。

        根据是否有异常发生，决定是否标记事务结束。

        参数:
        - exc_type: 异常类型，如果上下文管理器中的代码抛出了异常，则exc_type是非None。
        """
        if exc_type is not None:
            transaction_end(self.__id__, True)  # 如果有异常，标记事务异常结束
        else:
            transaction_end(self.__id__)  # 如果没有异常，标记事务正常结束

    def save(self, data: dict, status_code_mapper: Dict[int, int] = None, check=True):
        """
        保存数据到数据库。

        :param data: 需要保存的数据字典。
        :param status_code_mapper: 状态码映射器，用于将内部状态码映射为外部状态码。
        :param check: 是否进行数据完整性检查。
        :return: 保存操作的结果。
        """
        if status_code_mapper is None:
            status_code_mapper = {}
        return __check_res__(
            bridge.post("/storage/save", json=data, params={"tid": self.__id__}),
            status_code_mapper,
            check,
        )

    def search(
        self,
        data: dict,
        status_code_mapper: Dict[int, int] = None,
        check: bool = True,
    ):
        """
        根据给定条件搜索数据。

        :param data: 搜索条件的字典。
        :param status_code_mapper: 状态码映射器，用于将内部状态码映射为外部状态码。
        :param check: 是否进行数据完整性检查。
        :return: 搜索结果。
        """
        return __check_res__(
            bridge.post("/storage/search", json=data, params={"tid": self.__id__}),
            status_code_mapper,
            check,
        )

    def delete(
        self,
        data: dict,
        status_code_mapper: Dict[int, int] = None,
        check: bool = True,
    ):
        """
        删除符合给定条件的数据。

        :param data: 删除条件的字典。
        :param status_code_mapper: 状态码映射器，用于将内部状态码映射为外部状态码。
        :param check: 是否进行数据完整性检查。
        :return: 删除操作的结果。
        """
        return __check_res__(
            bridge.post("/storage/delete", json=data, params={"tid": self.__id__}),
            status_code_mapper,
            check,
        )

    def get(
        self,
        params: dict,
        status_code_mapper: Dict[int, int] = None,
        check: bool = True,
    ):
        """
        根据给定参数获取数据。

        :param params: 获取数据的参数字典。
        :param status_code_mapper: 状态码映射器，用于将内部状态码映射为外部状态码。
        :param check: 是否进行数据完整性检查。
        :return: 获取的数据。
        """
        return __check_res__(
            bridge.get("/storage/get", params={**params, "tid": self.__id__}),
            status_code_mapper,
            check,
        )


__default_ctx__ = TransactionContext()

save = __default_ctx__.save
delete = __default_ctx__.delete
search = __default_ctx__.search
get = __default_ctx__.get
