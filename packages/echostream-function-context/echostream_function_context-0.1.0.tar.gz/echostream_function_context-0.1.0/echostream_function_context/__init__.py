from logging import Logger
from typing import TYPE_CHECKING, BinaryIO, Literal, Union

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table
else:
    Table = object


class Context:

    config: dict
    logger: Logger
    node: str
    table: Table
    tenant: str

    @staticmethod
    def acquire(*args) -> None:
        pass

    @staticmethod
    def handle_bulk_data(
        data: Union[bytearray, bytes, BinaryIO],
        *,
        contentEncoding: Literal["deflate", "gzip"] = "gzip",
        useAccelerationEndpoint: bool = False
    ) -> str:
        pass

    @staticmethod
    def release() -> None:
        pass

    @staticmethod
    def locked() -> bool:
        pass
