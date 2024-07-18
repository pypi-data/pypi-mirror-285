import aio_pika.message
import functools
import logging
import msgpack
import pydantic
import zlib

from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar

from . import errors


logger = logging.getLogger(__name__)


TBaseModel = TypeVar("TBaseModel", bound="BaseModel")


class BaseModel(pydantic.BaseModel):
    @classmethod
    def model_validate_message(
        cls: Type[TBaseModel], message: aio_pika.message.Message
    ) -> "TBaseModel":
        body = message.body
        if message.content_encoding == "deflate":
            try:
                body = zlib.decompress(body)
            except Exception as error:
                raise errors.ParsingError(f"Message decompression failed: `{error!r}`")

        elif message.content_encoding:
            raise errors.ParsingError(
                f"Unknown content_encoding: `{message.content_encoding}`"
            )

        if message.content_type != "application/msgpack":
            raise errors.ParsingError(
                f"Got a message with unknown content type: {message.content_type}"
            )

        try:
            data = msgpack.loads(body, timestamp=3, ext_hook=msgpack_ext_hook)
            return cls.model_validate(data)
        except ValueError as error:
            raise errors.ParsingError(f"Message deserialization failed: `{error!r}`")

    def model_dump_msgpack(self, **kwargs) -> bytes:
        kwargs.setdefault("exclude_defaults", True)
        data = self.model_dump(**kwargs)
        return msgpack.dumps(data, datetime=True, default=msgpack_default)


class Request(BaseModel):
    method_name: str
    arguments: Dict[str, Any] = {}
    context: Optional[Any] = None
    timings: List[Tuple[str, float]] = []


class ResponseError(BaseModel):
    type: str
    message: Optional[str] = None


class Response(BaseModel):
    result: Optional[Any] = None
    error: Optional[ResponseError] = None
    context: Optional[Any] = None
    timings: List[Tuple[str, float]] = []

    @classmethod
    def wrap_errors(cls, func: Callable) -> Callable:
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            try:
                response = await func(*args, **kwargs)
                if not isinstance(response, cls):
                    raise TypeError(f"Incorrect response type, got: {type(response)}")

            except errors.RpcError as error:
                response = cls(
                    error={"type": type(error).__name__, "message": error.args[0]}
                )

            except Exception as error:
                logger.exception("Unhandled error")
                response = cls(error={"type": "UnhandledError", "message": repr(error)})

            return response

        return inner


ObjectId: Optional[Type] = None
try:
    from bson import ObjectId
except ImportError:
    pass


def msgpack_default(obj: Any) -> msgpack.ExtType:
    if ObjectId is not None and isinstance(obj, ObjectId):
        return msgpack.ExtType(1, obj.binary)

    raise TypeError(f"Cannot serialize {obj!r}")


def msgpack_ext_hook(code: int, data: bytes) -> Any:
    if code == 1:
        if ObjectId is None:
            raise RuntimeError("Install `bson` package to support `ObjectId` type")

        return ObjectId(data)

    return msgpack.ExtType(code, data)
