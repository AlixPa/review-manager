class SqliteNoConnectionError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class SqliteNoValueInsertionError(Exception):
    def __init__(self):
        super().__init__("No value given to insert.")


class SqliteColumnInconsistencyError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class SqliteDuplicateColumnUpdateError(Exception):
    def __init__(self, column: str):
        super().__init__(f"Updating multiple time the same column, {column=}")


class SqliteNoUpdateValuesError(Exception):
    def __init__(self):
        super().__init__("Nothing given to update.")


class SqliteWrongQueryError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class SqliteIdNotFoundError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)
