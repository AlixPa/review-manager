## NOTE: This client is async and should not be used with scripts, but with FAST API
import traceback
from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Literal, Type, TypeVar, overload
from uuid import uuid4

from sqlalchemy import CursorResult, text
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from src.config.mysql import mysql_config
from src.logger import get_logger
from src.models.database import BaseTableModel

from .exceptions import (
    AMySqlDuplicateError,
    AMySqlIdNotFoundError,
    AMySqlNoEngineError,
    AMySqlWrongQueryError,
)
from .models import CondReturn

base_logger = get_logger()
engine_reader = None
engine_writer = None


def _get_engine_reader() -> AsyncEngine:
    global engine_reader
    if engine_reader is None:
        engine_reader = create_async_engine(
            f"mysql+asyncmy://{mysql_config.user_reader}:{mysql_config.password_reader}@{mysql_config.host}:{mysql_config.port}/{mysql_config.database}",
            pool_size=5,
            max_overflow=5,
            pool_timeout=60,
            pool_recycle=1800,
        )
    return engine_reader


def _get_engine_writer() -> AsyncEngine:
    global engine_writer
    if engine_writer is None:
        engine_writer = create_async_engine(
            f"mysql+asyncmy://{mysql_config.user_writer}:{mysql_config.password_writer}@{mysql_config.host}:{mysql_config.port}/{mysql_config.database}",
            pool_size=5,
            max_overflow=5,
            pool_timeout=60,
            pool_recycle=1800,
        )
    return engine_writer


GenericTableModel = TypeVar("GenericTableModel", bound=BaseTableModel)


class AMysqlClient(ABC):
    def __init__(self, logger: Logger | None = None) -> None:
        self.logger = logger or base_logger
        self.engine: AsyncEngine | None = None

    @abstractmethod
    def _connect(self) -> None:
        """
        Sub-class should overwrite this method with correct credentials.
        """
        pass

    def _logging(self, query: str, args: dict | None, result: CursorResult) -> None:
        if args:
            for key, value in args.items():
                quoted = f"'{value}'" if isinstance(value, str) else str(value)
                query = query.replace(f":{key}", quoted)
        self.logger.debug(f"MysqlClient executed: {query} {result.rowcount=}")

    def _get_uuid4(self) -> str:
        return "id_" + str(uuid4()).replace("-", "_")

    def update_args_get_uids_sql(
        self, args: dict[str, Any], ls_val: list[Any]
    ) -> list[str]:
        uids = [self._get_uuid4() for _ in range(len(ls_val))]
        args.update({uid: value for uid, value in zip(uids, ls_val)})
        return [f":{uid}" for uid in uids]

    def _generate_cond(
        self,
        cond_null: list[str] = list(),
        cond_not_null: list[str] = list(),
        cond_in: dict[str, list] = dict(),
        cond_equal: dict[str, Any] = dict(),
        cond_non_equal: dict[str, Any] = dict(),
        cond_less_or_eq: dict[str, Any] = dict(),
        cond_greater_or_eq: dict[str, Any] = dict(),
        cond_less: dict[str, Any] = dict(),
        cond_greater: dict[str, Any] = dict(),
    ) -> CondReturn:
        """
        Function that generates the condition as well as the args for any query

        Returns
        -------
        str
            The condition Starting with WHERE of the sql query
        tuple
            The args parameter to give to MysqlClient.execute
        """
        conds = ["WHERE 1 = 1"]
        args: dict[str, Any] = dict()

        for col in cond_null:
            conds.append(f"AND {col} IS NULL")

        for col in cond_not_null:
            conds.append(f"AND {col} IS NOT NULL")

        for col, ls_val in cond_in.items():
            if len(ls_val) == 0:
                # No values in the in -> no match
                conds.append("AND 1 = 0")
                continue
            uids_sql = self.update_args_get_uids_sql(args=args, ls_val=ls_val)
            conds.append(f"AND {col} IN (" + ",".join(uids_sql) + ")")

        symbols_colvalues = {
            "=": cond_equal,
            "<>": cond_non_equal,
            "<=": cond_less_or_eq,
            ">=": cond_greater_or_eq,
            "<": cond_less,
            ">": cond_greater,
        }

        for symbol, colvalues in symbols_colvalues.items():
            for col, val in colvalues.items():
                uid = self._get_uuid4()
                conds.append(f"AND {col} {symbol} :{uid}")
                args[uid] = val

        return CondReturn(condition=" ".join(conds), args=args)

    async def execute(
        self, query: str, args: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Execute a SQL query and return the results, without commiting (read only).

        Parameters
        ----------
        query : str
            SQL query to execute
        args : tuple | dict | None, optional
            Parameters to pass to the query, by default None

        Returns
        -------
        list
            Results of the query execution

        Raises
        ------
        AMySqlWrongQueryError
            If query is wrong
        AMySqlNoEngineError
            If no database connection exists
        """
        if not self.engine:
            raise AMySqlNoEngineError("Could not execute query, no engine yet.")

        try:
            async with self.engine.connect() as conn:
                result_alchemy = await conn.execute(text(query), args or {})
                rows = result_alchemy.fetchall()
        except ProgrammingError:
            self.logger.warning(
                f"error while executing query, {traceback.format_exc()}"
            )
            raise AMySqlWrongQueryError(f"{traceback.format_exc()}")

        self._logging(query=query, args=args, result=result_alchemy)

        return [dict(r._mapping) for r in rows]

    async def count(
        self,
        table: Type[GenericTableModel],
        select_col: list[str] = list(),
        cond_null: list[str] = list(),
        cond_not_null: list[str] = list(),
        cond_in: dict[str, list] = dict(),
        cond_equal: dict[str, Any] = dict(),
        cond_non_equal: dict[str, Any] = dict(),
        cond_less_or_eq: dict[str, Any] = dict(),
        cond_greater_or_eq: dict[str, Any] = dict(),
        cond_less: dict[str, Any] = dict(),
        cond_greater: dict[str, Any] = dict(),
    ) -> int:
        """
        Execute a SELECT COUNT(...) query with various conditions.

        Parameters
        ----------
        table : Type[GenericTableModel]
            Table to query
        select_col : list[str], optional
            List of columns to include in the COUNT(...), by default all columns
        cond_null : list[str], optional
            Columns that must be NULL
        cond_not_null : list[str], optional
            Columns that must not be NULL
        cond_in : dict[str, list], optional
            Column values that must be in given list
        cond_eq : dict[str, Any], optional
            Column values that must equal given value
        cond_neq : dict[str, Any], optional
            Column values that must not equal given value
        cond_leq : dict[str, Any], optional
            Column values that must be less than or equal to given value
        cond_geq : dict[str, Any], optional
            Column values that must be greater than or equal to given value
        cond_l : dict[str, Any], optional
            Column values that must be less than given value
        cond_g : dict[str, Any], optional
            Column values that must be greater than given value

        Returns
        -------
        int
            result of the count

        Raises
        ------
        AMySqlWrongQueryError
            If query is wrong
        AMySqlNoEngineError
            If no database connection exists
        """
        query_parts = [
            f"SELECT COUNT({', '.join(select_col) if select_col else '*'}) AS ct FROM {table.__tablename__}"
        ]
        cond_ret = self._generate_cond(
            cond_equal=cond_equal,
            cond_greater=cond_greater,
            cond_greater_or_eq=cond_greater_or_eq,
            cond_in=cond_in,
            cond_less=cond_less,
            cond_less_or_eq=cond_less_or_eq,
            cond_non_equal=cond_non_equal,
            cond_not_null=cond_not_null,
            cond_null=cond_null,
        )
        cond, args = cond_ret.condition, cond_ret.args

        query_parts.append(cond)
        query_parts.append(";")

        res_mysql = await self.execute(query=" ".join(query_parts), args=args)
        res = res_mysql[0].get("ct", None)
        return int(str(res)) if res else -1

    async def select(
        self,
        table: Type[GenericTableModel],
        cond_null: list[str] = list(),
        cond_not_null: list[str] = list(),
        cond_in: dict[str, list] = dict(),
        cond_equal: dict[str, Any] = dict(),
        cond_non_equal: dict[str, Any] = dict(),
        cond_less_or_eq: dict[str, Any] = dict(),
        cond_greater_or_eq: dict[str, Any] = dict(),
        cond_less: dict[str, Any] = dict(),
        cond_greater: dict[str, Any] = dict(),
        order_by: str = "",
        ascending_order: bool = True,
        limit: int = 0,
        offset: int = 0,
    ) -> list[GenericTableModel]:
        """
        Execute a SELECT query with various conditions.

        Parameters
        ----------
        table : Type[T]
            Table class to query from
        select_col : list[str], optional
            List of columns to select, by default all columns. Note that this should not be used with a SqlModel expected return.
        cond_null : list[str], optional
            Columns that must be NULL
        cond_not_null : list[str], optional
            Columns that must not be NULL
        cond_in : dict[str, list], optional
            Column values that must be in given list
        cond_eq : dict[str, Any], optional
            Column values that must equal given value
        cond_neq : dict[str, Any], optional
            Column values that must not equal given value
        cond_leq : dict[str, Any], optional
            Column values that must be less than or equal to given value
        cond_geq : dict[str, Any], optional
            Column values that must be greater than or equal to given value
        cond_l : dict[str, Any], optional
            Column values that must be less than given value
        cond_g : dict[str, Any], optional
            Column values that must be greater than given value
        limit : int, optional
            Maximum number of rows to return, 0 means all, by default 0
        offset : int, optional
            Number of rows to skip before returning results, 0 means no offset, by default 0

        Returns
        -------
        list
            Query results as a list of actual class

        Raises
        ------
        AMySqlNoEngineError
            If no database connection exists
        AMySqlWrongQueryError
            If query is wrong
        """
        query_parts = [f"SELECT * FROM {table.__tablename__}"]
        cond_ret = self._generate_cond(
            cond_equal=cond_equal,
            cond_greater=cond_greater,
            cond_greater_or_eq=cond_greater_or_eq,
            cond_in=cond_in,
            cond_less=cond_less,
            cond_less_or_eq=cond_less_or_eq,
            cond_non_equal=cond_non_equal,
            cond_not_null=cond_not_null,
            cond_null=cond_null,
        )
        cond, args = cond_ret.condition, cond_ret.args

        query_parts.append(cond)

        if order_by:
            query_parts.append(
                f"ORDER BY {order_by} {'ASC' if ascending_order else 'DESC'}"
            )

        if limit > 0:
            query_parts.append(f"LIMIT {limit}")
            query_parts.append(f"OFFSET {offset}")
        query_parts.append(";")
        res_mysql = await self.execute(query=" ".join(query_parts), args=args)

        return [table(**r) for r in res_mysql]

    async def select_by_id(
        self,
        table: Type[GenericTableModel],
        id: int,
    ) -> GenericTableModel:
        """
        Select a row from a database table by its ID.

        Parameters
        ----------
        table : Type[T]
            Table class to query from
        id : int
            ID of the row to select

        Returns
        -------
        T
            Selected row as actual class

        Raises
        ------
        AMySqlNoEngineError
            If no database connection exists
        AMySqlWrongQueryError
            If query is wrong
        AMySqlIdNotFoundError
            If id not found in table
        """
        res_mysql = await self.select(
            table=table,
            cond_equal={"id": id},
        )
        if not res_mysql:
            raise AMySqlIdNotFoundError(
                f"{id=} not found during select in table {table if isinstance(table, str) else table.__tablename__}"
            )
        return res_mysql[0]

    async def id_exists(
        self,
        table: Type[GenericTableModel],
        id: int,
    ) -> bool:
        try:
            await self.select_by_id(table=table, id=id)
            return True
        except AMySqlIdNotFoundError:
            return False


class AMysqlClientReader(AMysqlClient):
    def __init__(self, logger: Logger | None = None) -> None:
        super().__init__(logger)
        self._connect()

    def _connect(self) -> None:
        self.engine = _get_engine_reader()

    async def check_alive(self) -> None:
        try:
            try:
                check_alive_res = await self.execute("select 1;")
            except Exception:
                check_alive_res = None
            if check_alive_res is None:
                self._connect()
            self.logger.info("AMysqlClientReader is alive.")
        except Exception:
            self.logger.critical("ERROR: Lost connection to Database.")
            raise AMySqlNoEngineError("ERROR: Lost connection to Database.")


class AMysqlClientWriter(AMysqlClient):
    def __init__(self, logger: Logger | None = None) -> None:
        super().__init__(logger)
        self._connect()

    def _connect(self) -> None:
        self.engine = _get_engine_writer()

    @overload
    async def execute(
        self,
        query: str,
        args: dict[str, Any] | None,
        insertion: Literal[True],
    ) -> int: ...

    @overload
    async def execute(
        self,
        query: str,
        args: dict[str, Any] | None = None,
        insertion: Literal[False] = False,
    ) -> list[dict[str, Any]]: ...

    async def execute(
        self,
        query: str,
        args: dict[str, Any] | None = None,
        insertion: bool = False,
    ) -> list[dict[str, Any]] | int:
        """
        Opens a transaction, execute a SQL query, commit and return the results.

        Parameters
        ----------
        query : str
            SQL query to execute
        args : tuple | dict | None, optional
            Parameters to pass to the query, by default None

        Returns
        -------
        list
            Results of the query execution

        Raises
        ------
        AMySqlWrongQueryError
            If query is wrong
        AMySqlNoEngineError
            If no database connection exists
        """
        if not self.engine:
            raise AMySqlNoEngineError("Could not execute query, no engine yet.")

        result_alchemy = None
        try:
            async with self.engine.begin() as conn:
                result_alchemy = await conn.execute(text(query), args or {})
                if insertion:
                    return result_alchemy.lastrowid
                else:
                    if result_alchemy.returns_rows:
                        rows = result_alchemy.fetchall()
                    else:
                        rows = list()
                    return [dict(r._mapping) for r in rows]
        except ProgrammingError:
            self.logger.warning(
                f"error while executing query, {traceback.format_exc()}"
            )
            raise AMySqlWrongQueryError(f"{traceback.format_exc()}")
        except IntegrityError as e:
            # MySQL duplicate key error code
            if getattr(e.orig, "args", None) and e.orig.args[0] == 1062:  # type:ignore
                raise AMySqlDuplicateError("Resource already exists")
            raise
        finally:
            if result_alchemy:
                self._logging(query=query, args=args, result=result_alchemy)

    async def insert_one(
        self,
        to_insert: BaseTableModel,
        or_ignore=False,
    ) -> None:
        """
        Insert a single row into a database table.
        Inline sets the id.

        Parameters
        ----------
        to_insert : T
            Item to insert
        or_ignore : bool, optional
            If True, use INSERT IGNORE, default False

        Raises
        ------
        AMySqlNoValueInsertionError
            If values dictionary is empty
        AMySqlNoEngineError
            If no database connection exists
        AMySqlWrongQueryError
            If query is wrong
        """
        await self.insert(
            to_insert=[to_insert],
            or_ignore=or_ignore,
        )

    async def insert(
        self,
        to_insert: list[GenericTableModel],
        or_ignore=False,
    ) -> None:
        """
        Insert multiple rows into a database table.
        Inline sets the ids.

        Parameters
        ----------
        to_insert : T
            List of items to insert
        or_ignore : bool, optional
            If True, use INSERT IGNORE, default False

        Raises
        ------
        AMySqlNoValueInsertionError
            If values dictionary is empty
        AMySqlNoEngineError
            If no database connection exists
        AMySqlWrongQueryError
            If query is wrong
        AMySqlColumnInconsistencyError
            If multiple rows have individually different columns
        """
        if not to_insert:
            return

        to_insert_dict = [
            e.model_dump(exclude={"createdAt", "updatedAt", "id"}) for e in to_insert
        ]

        cols = list(to_insert_dict[0].keys())
        query_parts = [
            f"INSERT {"IGNORE" if or_ignore else ""} INTO {to_insert[0].__tablename__}"
        ]
        query_parts.append(f"({",".join(cols)})")
        query_parts.append("VALUES")

        insert_part = list()
        args: dict[str, Any] = dict()
        for row in to_insert_dict:
            values = [row[col] for col in cols]
            uids_sql = self.update_args_get_uids_sql(args=args, ls_val=values)
            insert_part.append(f"({",".join(uids_sql)})")
        query_parts.append(",".join(insert_part))

        query_parts.append(";")

        first_id_inserted = await self.execute(
            query=" ".join(query_parts),
            args=args,
            insertion=True,
        )
        id_current = first_id_inserted
        for item in to_insert:
            item.id = id_current
            id_current += 1

    async def delete(
        self,
        table: Type[GenericTableModel],
        cond_null: list[str] = list(),
        cond_not_null: list[str] = list(),
        cond_in: dict[str, list] = dict(),
        cond_equal: dict[str, Any] = dict(),
        cond_non_equal: dict[str, Any] = dict(),
        cond_less_or_eq: dict[str, Any] = dict(),
        cond_greater_or_eq: dict[str, Any] = dict(),
        cond_less: dict[str, Any] = dict(),
        cond_greater: dict[str, Any] = dict(),
    ) -> list[GenericTableModel]:
        """
        Delete rows from a database table based on conditions and returns them.

        Parameters
        ----------
        table : Type[T]
            Table class to query from
        cond_null : list[str], optional
            Columns that must be NULL
        cond_not_null : list[str], optional
            Columns that must not be NULL
        cond_in : dict[str, list], optional
            Column values that must be in given list
        cond_eq : dict[str, Any], optional
            Column values that must equal given value
        cond_neq : dict[str, Any], optional
            Column values that must not equal given value
        cond_leq : dict[str, Any], optional
            Column values that must be less than or equal to given value
        cond_geq : dict[str, Any], optional
            Column values that must be greater than or equal to given value
        cond_l : dict[str, Any], optional
            Column values that must be less than given value
        cond_g : dict[str, Any], optional
            Column values that must be greater than given value

        Returns
        -------
        list
            Deleted rows as a list of actual class

        Raises
        ------
        AMySqlNoEngineError
            If no database connection exists
        AMySqlWrongQueryError
            If query is wrong
        """
        res_mysql = await self.select(
            table=table,
            cond_equal=cond_equal,
            cond_greater=cond_greater,
            cond_greater_or_eq=cond_greater_or_eq,
            cond_in=cond_in,
            cond_less=cond_less,
            cond_less_or_eq=cond_less_or_eq,
            cond_non_equal=cond_non_equal,
            cond_not_null=cond_not_null,
            cond_null=cond_null,
        )
        ids_to_delete_ls: list[int] = [r.id for r in res_mysql]

        if not ids_to_delete_ls:
            self.logger.info("nothing to update")
            return list()

        query_parts = [f"DELETE FROM {table.__tablename__}"]

        args: dict[str, Any] = dict()
        uids_sql = self.update_args_get_uids_sql(args=args, ls_val=ids_to_delete_ls)
        query_parts.append(f"WHERE id IN ({", ".join(uids_sql)})")
        query_parts.append(";")

        await self.execute(query=" ".join(query_parts), args=args)
        return res_mysql

    async def delete_by_id(
        self, table: Type[GenericTableModel], id: int
    ) -> GenericTableModel:
        """
        Delete a row from a database table by its ID.

        Parameters
        ----------
        table : Type[T]
            Table class to query from
        id : str
            ID of the row to delete

        Returns
        -------
        T
            Deleted row as actual class

        Raises
        ------
        AMySqlNoEngineError
            If no database connection exists
        AMySqlWrongQueryError
            If query is wrong
        AMySqlIdNotFoundError
            If id not found in table
        """
        res_mysql = await self.delete(table=table, cond_equal={"id": id})

        if not res_mysql:
            raise AMySqlIdNotFoundError(
                f"{id=} not found during delete in table {table.__tablename__}"
            )
        return res_mysql[0]

    async def update_by_id(
        self, table: Type[GenericTableModel], id: int, col_to_value_map: dict[str, Any]
    ) -> None:
        """
        Update a row from a database table by its ID.

        Parameters
        ----------
        table : Type[T]
            Table class to query from
        id : str
            ID of the row to update
        col_to_value_map : dict[str, Any]
            The dictionnary mapping the column names to the value to update

        Raises
        ------
        AMySqlNoEngineError
            If no database connection exists
        AMySqlWrongQueryError
            If query is wrong
        AMySqlIdNotFoundError
            If id not found in table
        """
        if not col_to_value_map:
            return

        if not await self.id_exists(table=table, id=id):
            raise AMySqlIdNotFoundError(
                f"{id=} not found during update in table {table.__tablename__}"
            )

        columns: list[str] = list()
        values: list[Any] = list()

        for col, val in col_to_value_map.items():
            columns.append(col)
            values.append(val)

        args: dict[str, Any] = dict()
        uuids_values = self.update_args_get_uids_sql(args=args, ls_val=values)

        await self.execute(
            query=f"""
            UPDATE {table.__tablename__}
            SET {",".join([f"{c}={u}" for c,u in zip(columns,uuids_values)])}
            WHERE 
                id={id}
        """,
            args=args,
        )
