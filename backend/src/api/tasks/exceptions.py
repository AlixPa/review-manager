class TaskNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CreatorNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TaskAndUserMismatch(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserNotReviewer(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PrLinkAlreadyExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
