from typing import Union, Dict, Any

import fastapi
from requests import Response


def check_res(
    res: Response,
    status_code_mapper: Union[Dict[int, int], None] = None,
):
    """
    根据响应对象检查HTTP请求的响应状态码。

    如果设置了status_code_mapper，则会根据映射关系返回相应的状态码；
    如果响应体是JSON格式，则将详细信息设为解析后的JSON对象；
    如果响应体是其他格式，则将详细信息设为响应体的文本内容。

    参数:
    - res: Response对象，包含HTTP请求的响应信息。
    - status_code_mapper: 字典类型，用于映射HTTP状态码。默认为None。

    返回:
    - Response对象，未经修改的响应对象。

    异常:
    - HTTPException: 如果状态码不在200-299范围内，且check为True，则抛出HTTPException异常。
    """
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


def assert_not_none(obj, status_code: int = 404, detail: Any | None = None):
    """
    断言对象不为None，如果为None，则抛出HTTPException异常。

    该函数用于验证传入的对象是否为None，如果为None，则根据指定的状态码和详细信息抛出HTTP异常。
    这对于在API开发中处理缺失的或预期的参数非常有用。

    参数:
    - obj: 需要验证的对象。
    - status_code: (可选) 默认为404。当obj为None时，抛出的HTTPException的状态码。
    - detail: (可选) 默认为None。当obj为None时，抛出的HTTPException的详细信息。

    抛出:
    - fastapi.HTTPException: 当obj为None时，抛出此异常。
    """
    if obj is None:
        raise fastapi.HTTPException(status_code=status_code, detail=detail)
    pass
