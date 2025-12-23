from uuid import UUID, uuid4


class UUID4Str(str):
    @classmethod
    def new(cls) -> "UUID4Str":
        return cls(str(uuid4()))

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if isinstance(v, UUID):
            u = v
        else:
            try:
                u = UUID(v, version=4)
            except Exception:
                raise ValueError("Must be a valid UUID4 string")
        if u.version != 4:
            raise ValueError("Must be UUID version 4")
        return str(u)
