from typing import Union, Dict

import fastapi
import requests_toolbelt.sessions
from requests import Response

session = requests_toolbelt.sessions.BaseUrlSession(base_url="http://localhost:10001")

post = session.post
delete = session.delete
get = session.get
put = session.put
patch = session.patch
head = session.head
options = session.options


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
