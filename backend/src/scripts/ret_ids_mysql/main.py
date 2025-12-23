import asyncio

from src.clients.mysql.async_client import AMysqlClientWriter
from src.clients.mysql.sync_client import MysqlClientWriter
from src.models.database import User


def update_test() -> None:
    mysql = MysqlClientWriter()
    mysql.start_transaction()
    to_insert = [
        User(name="qdq"),
        User(name="Fred"),
        User(name="Fred"),
        User(name="Fred"),
    ]
    print(to_insert)
    mysql.insert(to_insert=to_insert)
    print(to_insert)
    mysql.insert_one(to_insert=to_insert[0])
    print(to_insert)
    mysql.commit()


async def aupdate_test() -> None:
    amysql = AMysqlClientWriter()
    to_insert = [
        User(name="qdq"),
        User(name="Fred"),
        User(name="Fred"),
        User(name="Fred"),
    ]
    print(to_insert)
    await amysql.insert(to_insert=to_insert)
    print(to_insert)
    await amysql.insert_one(to_insert=to_insert[0])
    print(to_insert)


def main() -> None:
    print("---sync---")
    update_test()
    print("---async---")
    asyncio.run(aupdate_test())
