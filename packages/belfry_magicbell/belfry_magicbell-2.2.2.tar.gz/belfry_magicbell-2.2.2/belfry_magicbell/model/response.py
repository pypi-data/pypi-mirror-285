import typing

import orjson

from ._base import BaseModel

ResponseBodyT = typing.TypeVar("ResponseBodyT", bound=BaseModel)


class Response(BaseModel, typing.Generic[ResponseBodyT]):
    status_code: int
    content: bytes
    headers: typing.MutableMapping[str, str]
    parsed: typing.Optional[ResponseBodyT] = None

    def json_content(self) -> typing.Any:
        """Load `self.content` as JSON and return the parsed object"""
        return orjson.loads(self.content)
