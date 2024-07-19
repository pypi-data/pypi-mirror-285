from django.db import models

from django_pg_rrule.models import RecurrenceModel


class ExampleModel(RecurrenceModel):
    datetime_start = models.DateTimeField(null=True, blank=True)
    datetime_end = models.DateTimeField(null=True, blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
