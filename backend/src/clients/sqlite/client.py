import sqlite3
import threading
import traceback
from abc import ABC
from logging import Logger
from typing import Any, Literal, Type, TypeVar

from src.config.path import path_config
from src.logger import get_logger
from src.models.database import BaseTableModel

from .exceptions import (
    SqliteColumnInconsistencyError,
    SqliteDuplicateColumnUpdateError,
    SqliteIdNotFoundError,
    SqliteNoConnectionError,
    SqliteNoUpdateValuesError,
    SqliteNoValueInsertionError,
)

GenericTableModel = TypeVar("GenericTableModel", bound=BaseTableModel)

_thread_local = threading.local()


class SQLiteClient(ABC):
    def __init__(
        self,
        logger: Logger | None = None,
        isolation_level: Literal["DEFERRED"] | None = None,
    ) -> None:
        self.logger = logger or get_logger("SQLiteClient-logger")
        self.connection: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None
        assert isolation_level in {"DEFERRED", None}
        self._isolation_level = isolation_level
        self._connect()

    def _connect(self) -> None:
        connection_identifier = f"sqlite_connection_{self._isolation_level or 'NONE'}"

        if not hasattr(_thread_local, connection_identifier):
            conn = sqlite3.connect(
                path_config.sqlite_db_file,
                check_same_thread=False,
                isolation_level=self._isolation_level,  # type: ignore
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            setattr(_thread_local, connection_identifier, conn)

        self.connection = getattr(_thread_local, connection_identifier)

    def _logging(
        self, cursor: sqlite3.Cursor, query: str, params: tuple | None
    ) -> None:
        self.logger.debug(
            f"SQLiteClient executed: {cursor.rowcount=}, {query=}, {params=}"
        )

    def _generate_cond(
        self,
        cond_null: list[str] = list(),
        cond_not_null: list[str] = list(),
        cond_in: dict[str, list] = dict(),
        cond_equal: dict[str, object] = dict(),
        cond_non_equal: dict[str, object] = dict(),
        cond_less_or_eq: dict[str, object] = dict(),
        cond_greater_or_eq: dict[str, object] = dict(),
        cond_less: dict[str, object] = dict(),
        cond_greater: dict[str, object] = dict(),
    ) -> tuple[str, tuple]:
        """
        Function that generates the condition as well as the args for any query

        Returns
        -------
        str
            The condition Starting with WHERE of the sql query
        tuple
            The args parameter to give to SqlClient.execute
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
            conds.append(f"AND {col} IN (" + ",".join(["?"] * len(ls_val)) + ")")
            args.extend(ls_val)

        for col, val in cond_equal.items():
            conds.append(f"AND {col} = ?")
            args.append(val)

        for col, val in cond_non_equal.items():
            conds.append(f"AND {col} <> ?")
            args.append(val)

        for col, val in cond_less_or_eq.items():
            conds.append(f"AND {col} <= ?")
            args.append(val)

        for col, val in cond_greater_or_eq.items():
            conds.append(f"AND {col} >= ?")
            args.append(val)

        for col, val in cond_less.items():
            conds.append(f"AND {col} < ?")
            args.append(val)

        for col, val in cond_greater.items():
            conds.append(f"AND {col} > ?")
            args.append(val)

        return " ".join(conds), tuple(args)

    def execute(self, query: str, args: tuple | None = None) -> list[dict[str, Any]]:
        """
        Execute a SQL query and return the results.

        Parameters
        ----------
        query : str
            SQL query to execute
        args : tuple | None, optional
            Parameters to pass to the query, by default None

        Returns
        -------
        tuple
            Results of the query execution
        """
        if not self.connection:
            raise SqliteNoConnectionError("Could not execute query, no connection yet.")
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute(query, args or ())
            res = self.cursor.fetchall()
        except Exception:
            self.logger.warning(
                f"error while executing query, {traceback.format_exc()}"
            )
            raise
        self._logging(self.cursor, query, args)
        self.cursor.close()
        self.cursor = None
        return res

    def count(
        self,
        table: Type[GenericTableModel],
        select_col: list[str] = list(),
        cond_null: list[str] = list(),
        cond_not_null: list[str] = list(),
        cond_in: dict[str, list] = dict(),
        cond_equal: dict[str, object] = dict(),
        cond_non_equal: dict[str, object] = dict(),
        cond_less_or_eq: dict[str, object] = dict(),
        cond_greater_or_eq: dict[str, object] = dict(),
        cond_less: dict[str, object] = dict(),
        cond_greater: dict[str, object] = dict(),
    ) -> int:
        """
        Execute a SELECT COUNT(...) query with various conditions.

        Parameters
        ----------
        table : str
            Table to query
        select_col : list[str], optional
            List of columns to include in the COUNT(...), by default all columns
        cond_null : list[str], optional
            Columns that must be NULL
        cond_not_null : list[str], optional
            Columns that must not be NULL
        cond_in : dict[str, list], optional
            Column values that must be in given list
        cond_eq : dict[str, object], optional
            Column values that must equal given value
        cond_neq : dict[str, object], optional
            Column values that must not equal given value
        cond_leq : dict[str, object], optional
            Column values that must be less than or equal to given value
        cond_geq : dict[str, object], optional
            Column values that must be greater than or equal to given value
        cond_l : dict[str, object], optional
            Column values that must be less than given value
        cond_g : dict[str, object], optional
            Column values that must be greater than given value

        Returns
        -------
        int
            result of the count
        None
            if query went wrong
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

        res_Sql = self.execute(query=" ".join(query_parts), args=args)
        res = res_Sql[0]["ct"]
        return int(str(res))

    def select(
        self,
        table: Type[GenericTableModel],
        cond_null: list[str] = list(),
        cond_not_null: list[str] = list(),
        cond_in: dict[str, list] = dict(),
        cond_equal: dict[str, object] = dict(),
        cond_non_equal: dict[str, object] = dict(),
        cond_less_or_eq: dict[str, object] = dict(),
        cond_greater_or_eq: dict[str, object] = dict(),
        cond_less: dict[str, object] = dict(),
        cond_greater: dict[str, object] = dict(),
        order_by: str = "",
        ascending_order: bool = True,
        limit: int = 0,
        offset: int = 0,
    ) -> list[GenericTableModel]:
        """
        Execute a SELECT query with various conditions.

        Parameters
        ----------
        table : str | Type[T]
            Table name or actual table class to query from
        cond_null : list[str], optional
            Columns that must be NULL
        cond_not_null : list[str], optional
            Columns that must not be NULL
        cond_in : dict[str, list], optional
            Column values that must be in given list
        cond_eq : dict[str, object], optional
            Column values that must equal given value
        cond_neq : dict[str, object], optional
            Column values that must not equal given value
        cond_leq : dict[str, object], optional
            Column values that must be less than or equal to given value
        cond_geq : dict[str, object], optional
            Column values that must be greater than or equal to given value
        cond_l : dict[str, object], optional
            Column values that must be less than given value
        cond_g : dict[str, object], optional
            Column values that must be greater than given value
        limit : int, optional
            Maximum number of rows to return, 0 means all, by default 0
        offset : int, optional
            Number of rows to skip before returning results, 0 means no offset, by default 0

        Returns
        -------
        tuple
            Query results as a tuple of dictionaries or actual class if given
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
        res_Sql = self.execute(query=" ".join(query_parts), args=args)
        return list(table(**r) for r in res_Sql)

    def select_by_id(
        self,
        table: Type[GenericTableModel],
        id: str,
    ) -> GenericTableModel:
        """
        Select a row from a database table by its ID.

        Parameters
        ----------
        table : str | Type[T]
            Table name or actual table class to query from
        id : str
            ID of the row to select

        Returns
        -------
        dict[str, object] | T
            Selected row as a dictionnary or actual class if given
        """
        res_Sql = self.select(
            table=table,
            cond_equal={"id": id},
        )
        if not res_Sql:
            raise SqliteIdNotFoundError(
                f"{id=} not found during select in table {table.__tablename__}"
            )
        return res_Sql[0]

    def id_exists(
        self,
        table: Type[GenericTableModel],
        id: str,
    ) -> bool:
        try:
            self.select_by_id(table=table, id=id)
            return True
        except SqliteIdNotFoundError:
            return False

    def start_transaction(self) -> None:
        self._connect()

    def commit(self) -> None:
        """
        Commits the transaction.
        """
        if not self.connection:
            raise SqliteNoConnectionError("Cannot commit if transaction is closed.")
        self.connection.commit()

    def rollback(self) -> None:
        """
        Rollback the transaction.
        """
        if not self.connection:
            raise SqliteNoConnectionError("Cannot commit if transaction is closed.")
        self.connection.rollback()

    def insert_one(
        self,
        table: Type[GenericTableModel],
        to_insert: GenericTableModel,
        or_ignore=False,
    ) -> None:
        """
        Insert a single row into a database table.

        Parameters
        ----------
        table: GenericTableModel
            Table to insert into
        to_insert : dict
            Dictionary of column names and their corresponding values
        or_ignore : bool, optional
            If True, use INSERT IGNORE, default False
        """
        self.insert(
            table=table,
            to_insert=[to_insert],
            or_ignore=or_ignore,
        )

    def insert(
        self,
        table: Type[GenericTableModel],
        to_insert: list[GenericTableModel],
        or_ignore=False,
    ) -> None:
        """
        Insert multiple rows into a database table.

        Parameters
        ----------
        table: GenericTableModel
            Table to insert into
        to_insert : list[dict[str, object]]
            List of dictionary of column names and their corresponding values
        or_ignore : bool, optional
            If True, use INSERT IGNORE, default False
        """
        to_insert_dict = [e.model_dump() for e in to_insert]

        for row in to_insert_dict:
            if "createdAt" in row:
                del row["createdAt"]
            if "updatedAt" in row:
                del row["updatedAt"]

        to_insert_dict = [row for row in to_insert_dict if row]
        if not to_insert_dict:
            raise SqliteNoValueInsertionError()

        cols = set(to_insert_dict[0].keys())
        for row in to_insert_dict:
            for col in cols:
                if not col in row:
                    raise SqliteColumnInconsistencyError(
                        f"{col=} is not in one of the row to insert: {row=}"
                    )
            for col in row:
                if not col in cols:
                    raise SqliteColumnInconsistencyError(
                        f"{col=} is not in the first row to insert: col_of_first_row={cols}"
                    )
        cols = list(cols)

        query_parts = [
            f"INSERT {"OR IGNORE" if or_ignore else ""} INTO {table.__tablename__}"
        ]
        query_parts.append(f"({",".join(cols)})")
        query_parts.append("VALUES")

        insert_part = list()
        args = list()
        for row in to_insert_dict:
            insert_part.append(f"({",".join(["?"] * len(cols))})")
            args.extend([row[col] for col in cols])
        query_parts.append(",".join(insert_part))

        query_parts.append(";")

        self.execute(
            query=" ".join(query_parts),
            args=tuple(args),
        )

    def update_by_id(
        self,
        table: Type[GenericTableModel],
        id: str,
        update_col_col: dict[str, str] = dict(),
        update_col_value: dict[str, object] = dict(),
    ) -> None:
        """
        Update a single row in a table by its ID.

        Parameters
        ----------
        table: GenericTableModel
            Table to update
        id : str
            ID of the row to update
        update_col_col : dict[str, str], optional
            Dictionary mapping columns to update with other column values
        update_col_value : dict[str, object], optional
            Dictionary mapping columns to update with specific values
        """
        if not self.id_exists(table=table, id=id):
            raise SqliteIdNotFoundError(
                f"{id=} not found during update in table {table if isinstance(table, str) else table.__tablename__}"
            )
        for col in update_col_value:
            if col in update_col_col:
                raise SqliteDuplicateColumnUpdateError(
                    f"Duplicates column in update statement. {col=} is in both update_col_value and update_col_col."
                )
        for col in update_col_col:
            if col in update_col_value:
                raise SqliteDuplicateColumnUpdateError(
                    f"Duplicates column in update statement. {col=} is in both update_col_value and update_col_col."
                )

        if not update_col_col and not update_col_value:
            raise SqliteNoUpdateValuesError()

        query_parts = [f"UPDATE {table.__tablename__}"]
        query_parts.append("SET")

        col_col_parts: list[str] = list()
        for col_dst, col_src in update_col_col.items():
            col_col_parts.append(f"{col_dst}={col_src}")
        query_parts.append(",".join(col_col_parts))

        col_val_parts: list[str] = list()
        values = list()
        for col_dst, value in update_col_value.items():
            col_val_parts.append(f"{col_dst}=?")
            values.append(value)
        query_parts.append(",".join(col_val_parts))

        query_parts.append(f"WHERE id=?")
        values.append(id)
        query_parts.append(";")

        self.execute(query=" ".join(query_parts), args=tuple(values))

    def delete(
        self,
        table: Type[GenericTableModel],
        cond_null: list[str] = list(),
        cond_not_null: list[str] = list(),
        cond_in: dict[str, list] = dict(),
        cond_equal: dict[str, object] = dict(),
        cond_non_equal: dict[str, object] = dict(),
        cond_less_or_eq: dict[str, object] = dict(),
        cond_greater_or_eq: dict[str, object] = dict(),
        cond_less: dict[str, object] = dict(),
        cond_greater: dict[str, object] = dict(),
    ) -> list[GenericTableModel]:
        """
        Delete rows from a database table based on conditions and returns them.

        Parameters
        ----------
        table : str | Type[T]
            Table name or actual table class to query from
        cond_null : list[str], optional
            Columns that must be NULL
        cond_not_null : list[str], optional
            Columns that must not be NULL
        cond_in : dict[str, list], optional
            Column values that must be in given list
        cond_eq : dict[str, object], optional
            Column values that must equal given value
        cond_neq : dict[str, object], optional
            Column values that must not equal given value
        cond_leq : dict[str, object], optional
            Column values that must be less than or equal to given value
        cond_geq : dict[str, object], optional
            Column values that must be greater than or equal to given value
        cond_l : dict[str, object], optional
            Column values that must be less than given value
        cond_g : dict[str, object], optional
            Column values that must be greater than given value

        Returns
        -------
        tuple
            Deleted rows as a tuple of dictionaries or actual class if given
        """
        res_Sql = self.select(
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
        ids_to_delete_ls: list[int] = [r.id for r in res_Sql]

        if not ids_to_delete_ls:
            self.logger.info("nothing to update")
            return list()

        query_parts = [f"DELETE FROM {table.__tablename__}"]
        query_parts.append(f"WHERE id IN ({", ".join(["?"]*len(ids_to_delete_ls))})")
        query_parts.append(";")

        self.execute(query=" ".join(query_parts), args=tuple(ids_to_delete_ls))
        return res_Sql

    def delete_by_id(
        self, table: Type[GenericTableModel], id: str
    ) -> GenericTableModel:
        """
        Delete a row from a database table by its ID.

        Parameters
        ----------
        table : str | Type[T]
            Table name or actual table class to query from
        id : str
            ID of the row to delete

        Returns
        -------
        dict[str, object] | T
            Deleted row as a dictionnary or actual class if given
        """
        res_Sql = self.delete(table=table, cond_equal={"id": id})

        if not res_Sql:
            raise SqliteIdNotFoundError(
                f"{id=} not found during delete in table {table.__tablename__}"
            )
        return res_Sql[0]
