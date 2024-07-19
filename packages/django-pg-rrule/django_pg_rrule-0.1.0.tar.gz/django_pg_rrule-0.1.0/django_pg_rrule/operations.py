from django.contrib.postgres.operations import CreateExtension


class RruleExtension(CreateExtension):
    def __init__(self):
        self.name = "pg_rrule"
