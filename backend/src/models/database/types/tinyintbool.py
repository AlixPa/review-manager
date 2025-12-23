from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer

TinyBool = Annotated[
    bool,
    BeforeValidator(lambda v: bool(int(v))),  # input: 0/1 -> bool
    PlainSerializer(lambda v: 1 if v else 0),  # output: bool -> 0/1
]
