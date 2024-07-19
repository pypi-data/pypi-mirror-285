from datetime import datetime, timedelta, timezone, date

from .test_app.models import ExampleModel
import pytest

pytestmark = pytest.mark.django_db


def test_datetimes():
    e = ExampleModel.objects.create(
        datetime_start=datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc),
        datetime_end=datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc),
        rrule="FREQ=WEEKLY;COUNT=24",
    )

    qs = ExampleModel.objects.with_occurrences().order_by("odatetime")

    assert qs.count() == 24

    current_datetime = e.datetime_start
    for el in qs:
        assert el.odatetime == current_datetime
        current_datetime += timedelta(days=7)


def test_exdatetimes():
    e = ExampleModel.objects.create(
        datetime_start=datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc),
        datetime_end=datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc),
        exdatetimes=[datetime(2024, 1, 8, 8, 0, tzinfo=timezone.utc)],
        rrule="FREQ=WEEKLY;COUNT=3",
    )

    qs = (
        ExampleModel.objects.with_occurrences()
        .order_by("odatetime")
        .values_list("odatetime", flat=True)
    )

    assert qs.count() == 2
    assert e.exdatetimes[0] not in qs


def test_rdatetimes():
    e = ExampleModel.objects.create(
        datetime_start=datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc),
        datetime_end=datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc),
        rrule="FREQ=WEEKLY;COUNT=3",
        rdatetimes=[datetime(2024, 1, 7, 8, 0, tzinfo=timezone.utc)],
    )

    qs = (
        ExampleModel.objects.with_occurrences()
        .order_by("odatetime")
        .values_list("odatetime", flat=True)
    )

    assert qs.count() == 4
    assert e.rdatetimes[0] in qs


def test_dates():
    e = ExampleModel.objects.create(
        date_start=date(
            2024,
            1,
            1,
        ),
        date_end=date(
            2024,
            1,
            1,
        ),
        rrule="FREQ=WEEKLY;COUNT=24",
    )

    qs = ExampleModel.objects.with_occurrences().order_by("odate")

    assert qs.count() == 24

    current_date = e.date_start
    for el in qs:
        assert el.odate == current_date
        current_date += timedelta(days=7)


def test_exdates():
    e = ExampleModel.objects.create(
        date_start=date(2024, 1, 1),
        date_end=date(2024, 1, 1),
        exdates=[date(2024, 1, 8)],
        rrule="FREQ=WEEKLY;COUNT=3",
    )

    qs = (
        ExampleModel.objects.with_occurrences()
        .order_by("odate")
        .values_list("odate", flat=True)
    )

    assert qs.count() == 2
    assert e.exdates[0] not in qs


def test_rdates():
    e = ExampleModel.objects.create(
        date_start=date(2024, 1, 1),
        date_end=date(2024, 1, 1),
        rrule="FREQ=WEEKLY;COUNT=3",
        rdates=[date(2024, 1, 7)],
    )

    qs = (
        ExampleModel.objects.with_occurrences()
        .order_by("odate")
        .values_list("odate", flat=True)
    )

    assert qs.count() == 4
    assert e.rdates[0] in qs
