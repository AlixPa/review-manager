## NOTE: This client is sync and should not be used with FAST API, but with scripts
import traceback
from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Literal, Type, TypeVar, overload

import pymysql.cursors
from src.config.mysql import mysql_config
from src.logger import get_logger
from src.models.database import BaseTableModel

from .exceptions import (
    MySqlIdNotFoundError,
    MySqlNoConnectionError,
    MySqlWrongQueryError,
)

base_logger = get_logger()
GenericTableModel = TypeVar("GenericTableModel", bound=BaseTableModel)


class MysqlClient(ABC):
    def __init__(self, logger: Logger | None = None) -> None:
        self.logger = logger or base_logger
        self.connection: pymysql.Connection[pymysql.cursors.DictCursor] | None = None

    @abstractmethod
    def _connect(self) -> None:
        """
        Sub-class should overwrite this method with correct credentials.
        """
        pass

    def _logging(self, cursor) -> None:
        self.logger.debug(
            f"MysqlClient executed: {str(cursor._executed)} {cursor.rowcount=}"
        )

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
    ) -> tuple[str, tuple]:
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
        args = list()

        for col in cond_null:
            conds.append(f"AND {col} IS NULL")

        for col in cond_not_null:
            conds.append(f"AND {col} IS NOT NULL")

        for col, ls_val in cond_in.items():
            if len(ls_val) == 0:
                # No values in the in -> no match
                conds.append("AND 1 = 0")
                continue
            conds.append(f"AND {col} IN (" + ",".join(["%s"] * len(ls_val)) + ")")
            args.extend(ls_val)

        for col, val in cond_equal.items():
            conds.append(f"AND {col} = %s")
            args.append(val)

        for col, val in cond_non_equal.items():
            conds.append(f"AND {col} <> %s")
            args.append(val)

        for col, val in cond_less_or_eq.items():
            conds.append(f"AND {col} <= %s")
            args.append(val)

        for col, val in cond_greater_or_eq.items():
            conds.append(f"AND {col} >= %s")
            args.append(val)

        for col, val in cond_less.items():
            conds.append(f"AND {col} < %s")
            args.append(val)

        for col, val in cond_greater.items():
            conds.append(f"AND {col} > %s")
            args.append(val)

        return " ".join(conds), tuple(args)

    @overload
    def execute(
        self,
        query: str,
        args: tuple | dict | None,
        insertion: Literal[True],
    ) -> int: ...

    @overload
    def execute(
        self,
        query: str,
        args: tuple | dict | None = None,
        insertion: Literal[False] = False,
    ) -> tuple[dict[str, Any], ...]: ...

    def execute(
        self,
        query: str,
        args: tuple | dict | None = None,
        insertion: bool = False,
    ) -> tuple[dict[str, Any], ...] | int:
        """
        Execute a SQL query and return the results.

        Parameters
        ----------
        query : str
            SQL query to execute
        args : tuple | dict | None, optional
            Parameters to pass to the query, by default None

        Returns
        -------
        tuple
            Results of the query execution

        Raises
        ------
        NoConnectionError
            If no database connection exists
        MySqlWrongQueryError
            If query is wrong
        MySqlNoConnectionError
            If no database connection exists
        """
        if not self.connection:
            raise MySqlNoConnectionError("Could not execute query, no connection yet.")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query=query, args=args)
                if insertion:
                    return cursor.lastrowid
                else:
                    return cursor.fetchall()
            except pymysql.err.ProgrammingError as e:
                self.logger.warning(
                    f"error while executing query, {traceback.format_exc()}"
                )
                raise MySqlWrongQueryError(f"{traceback.format_exc()}")
            finally:
                self._logging(cursor)

    def count(
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
        table : Type[T]
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
        MySqlWrongQueryError
            If query is wrong
        MySqlNoConnectionError
            If no database connection exists
        """
        query_parts = [
            f"SELECT COUNT({', '.join(select_col) if select_col else '*'}) AS ct FROM {table.__tablename__}"
        ]
        cond, args = self._generate_cond(
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

        query_parts.append(cond)
        query_parts.append(";")

        res_mysql = self.execute(query=" ".join(query_parts), args=args)
        res = res_mysql[0].get("ct", None)
        return int(str(res)) if res else -1

    def select(
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
    ) -> tuple[GenericTableModel, ...]:
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
        tuple
            Query results as actual class

        Raises
        ------
        MySqlNoConnectionError
            If no database connection exists
        MySqlWrongQueryError
            If query is wrong
        """
        query_parts = [f"SELECT * FROM {table.__tablename__}"]
        cond, args = self._generate_cond(
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
        query_parts.append(cond)
        if order_by:
            query_parts.append(
                f"ORDER BY {order_by} {'ASC' if ascending_order else 'DESC'}"
            )
        if limit > 0:
            query_parts.append(f"LIMIT {limit}")
            query_parts.append(f"OFFSET {offset}")
        query_parts.append(";")
        res_mysql = self.execute(query=" ".join(query_parts), args=args)
        return tuple(table(**r) for r in res_mysql)

    def select_by_id(
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
        MySqlNoConnectionError
            If no database connection exists
        MySqlWrongQueryError
            If query is wrong
        MySqlIdNotFoundError
            If id not found in table
        """
        res_mysql = self.select(
            table=table,
            cond_equal={"id": id},
        )
        if not res_mysql:
            raise MySqlIdNotFoundError(
                f"{id=} not found during select in table {table if isinstance(table, str) else table.__tablename__}"
            )
        return res_mysql[0]

    def id_exists(
        self,
        table: Type[GenericTableModel],
        id: int,
    ) -> bool:
        try:
            self.select_by_id(table=table, id=id)
            return True
        except MySqlIdNotFoundError:
            return False


class MysqlClientReader(MysqlClient):
    def __init__(self, logger: Logger | None = None) -> None:
        super().__init__(logger)
        self._connect()

    def _connect(self) -> None:
        self.connection = pymysql.connect(
            host=mysql_config.host,
            port=mysql_config.port,
            user=mysql_config.user_reader,
            password=mysql_config.password_reader,
            database=mysql_config.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def check_alive(self) -> None:
        try:
            try:
                check_alive_res = self.execute("select 1;")
            except Exception:
                check_alive_res = None
            if check_alive_res is None:
                self._connect()
            self.logger.info("MysqlClientReader is alive.")
        except Exception:
            self.logger.critical("ERROR: Lost connection to Database.")
            raise MySqlNoConnectionError("ERROR: Lost connection to Database.")

    def close(self) -> None:
        if self.connection:
            self.connection.close()


class MysqlClientWriter(MysqlClient):
    def __init__(self, logger: Logger | None = None) -> None:
        super().__init__(logger)

    def _connect(self) -> None:
        self.connection = pymysql.connect(
            host=mysql_config.host,
            port=mysql_config.port,
            user=mysql_config.user_writer,
            password=mysql_config.password_writer,
            database=mysql_config.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def start_transaction(self) -> None:
        self._connect()

    def commit(self) -> None:
        """
        Commits the transaction and close the connection.
        """
        if not self.connection:
            raise MySqlNoConnectionError("Cannot commit if transaction is closed.")
        self.connection.commit()
        self.connection.close()

    def rollback(self) -> None:
        """
        Rollback the transaction and close the connection.
        """
        if not self.connection:
            raise MySqlNoConnectionError("Cannot commit if transaction is closed.")
        self.connection.rollback()
        self.connection.close()

    def insert_one(
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
        MySqlNoValueInsertionError
            If values dictionary is empty
        MySqlNoConnectionError
            If no database connection exists
        MySqlWrongQueryError
            If query is wrong
        """
        self.insert(
            to_insert=[to_insert],
            or_ignore=or_ignore,
        )

    def insert(
        self,
        to_insert: list[GenericTableModel],
        or_ignore=False,
    ) -> None:
        """
        Insert multiple rows into a database table.
        Inline sets the ids.

        Parameters
        ----------
        to_insert : list[T]
            List of items to insert
        or_ignore : bool, optional
            If True, use INSERT IGNORE, default False

        Raises
        ------
        MySqlNoValueInsertionError
            If values dictionary is empty
        MySqlNoConnectionError
            If no database connection exists
        MySqlWrongQueryError
            If query is wrong
        MySqlColumnInconsistencyError
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
        args = list()
        for row in to_insert_dict:
            insert_part.append(f"({",".join(["%s"] * len(cols))})")
            args.extend([row[col] for col in cols])
        query_parts.append(",".join(insert_part))

        query_parts.append(";")

        first_id_inserted = self.execute(
            query=" ".join(query_parts),
            args=tuple(args),
            insertion=True,
        )

        id_current = first_id_inserted
        for item in to_insert:
            item.id = id_current
            id_current += 1

    def delete(
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
    ) -> tuple[GenericTableModel, ...]:
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
        tuple
            Deleted rows as actual class

        Raises
        ------
        MySqlNoConnectionError
            If no database connection exists
        MySqlWrongQueryError
            If query is wrong
        """
        res_mysql = self.select(
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
            self.logger.info("nothing to delete")
            return tuple()

        query_parts = [f"DELETE FROM {table.__tablename__}"]
        query_parts.append(f"WHERE id IN ({", ".join(["%s"]*len(ids_to_delete_ls))})")
        query_parts.append(";")

        self.execute(query=" ".join(query_parts), args=tuple(ids_to_delete_ls))
        return res_mysql

    def delete_by_id(
        self,
        table: Type[GenericTableModel],
        id: int,
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
        MySqlNoConnectionError
            If no database connection exists
        MySqlWrongQueryError
            If query is wrong
        MySqlIdNotFoundError
            If id not found in table
        """
        res_mysql = self.delete(table=table, cond_equal={"id": id})

        if not res_mysql:
            raise MySqlIdNotFoundError(
                f"{id=} not found during delete in table {table if isinstance(table, str) else table.__tablename__}"
            )
        return res_mysql[0]
