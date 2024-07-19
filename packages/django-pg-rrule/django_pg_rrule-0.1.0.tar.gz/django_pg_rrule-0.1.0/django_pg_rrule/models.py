from django.db import models
from django.contrib.postgres.fields import ArrayField

from django_pg_rrule.managers import RecurrenceManager


class RecurrenceModel(models.Model):
    objects = RecurrenceManager()

    rrule = models.TextField(null=True, blank=True)
    rdates = ArrayField(models.DateField(), default=[], blank=True)
    rdatetimes = ArrayField(models.DateTimeField(), default=[], blank=True)
    exdates = ArrayField(models.DateField(), default=[], blank=True)
    exdatetimes = ArrayField(models.DateTimeField(), default=[], blank=True)

    class Meta:
        abstract = True
