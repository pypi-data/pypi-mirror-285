import uuid
from typing import Dict

import bridge


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
    res = bridge.post(
        "/storage/collection/default",
        params={"type": _type, "tid": tid},
    )
    if check:
        bridge.check_res(
            res,
            status_code_mapper,
        )
    return res


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
    res = bridge.post(
        "/storage/transaction/end",
        params={"tid": tid, "rollback": rollback},
    )
    if check:
        bridge.check_res(
            res,
            status_code_mapper,
        )
    return res


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
        res = bridge.post("/storage/save", json=data, params={"tid": self.__id__})
        if check:
            bridge.check_res(
                res,
                status_code_mapper,
            )
        return res

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
        res = bridge.post("/storage/search", json=data, params={"tid": self.__id__})
        if check:
            bridge.check_res(
                res,
                status_code_mapper,
            )
        return res

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
        res = bridge.post("/storage/delete", json=data, params={"tid": self.__id__})
        if check:
            bridge.check_res(
                res,
                status_code_mapper,
            )
        return res

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
        res = bridge.get("/storage/get", params={**params, "tid": self.__id__})
        if check:
            bridge.check_res(
                res,
                status_code_mapper,
            )
        return res


__default_ctx__ = TransactionContext()

save = __default_ctx__.save
delete = __default_ctx__.delete
search = __default_ctx__.search
get = __default_ctx__.get
