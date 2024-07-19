from typing import Any
from django.db.models import CharField


class RruleField(CharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["max_length"] = 255
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return "rrule"
