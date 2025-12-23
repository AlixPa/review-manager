class AMySqlNoEngineError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class AMySqlNoValueInsertionError(Exception):
    def __init__(self):
        super().__init__("No value given to insert.")


class AMySqlColumnInconsistencyError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class AMySqlDuplicateColumnUpdateError(Exception):
    def __init__(self, column: str):
        super().__init__(f"Updating multiple time the same column, {column=}")


class AMySqlNoUpdateValuesError(Exception):
    def __init__(self):
        super().__init__("Nothing given to update.")


class AMySqlWrongQueryError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class AMySqlIdNotFoundError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)


class AMySqlDuplicateError(Exception):
    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)
