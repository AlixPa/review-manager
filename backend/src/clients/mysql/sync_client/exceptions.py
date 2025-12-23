class MySqlNoConnectionError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class MySqlNoValueInsertionError(Exception):
    def __init__(self):
        super().__init__("No value given to insert.")


class MySqlColumnInconsistencyError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class MySqlDuplicateColumnUpdateError(Exception):
    def __init__(self, column: str):
        super().__init__(f"Updating multiple time the same column, {column=}")


class MySqlNoUpdateValuesError(Exception):
    def __init__(self):
        super().__init__("Nothing given to update.")


class MySqlWrongQueryError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class MySqlIdNotFoundError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)
