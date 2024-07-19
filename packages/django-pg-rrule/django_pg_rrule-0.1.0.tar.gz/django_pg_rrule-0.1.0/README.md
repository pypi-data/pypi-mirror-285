# django-pg-rrule

django-pg-rrule provides Django support for the PostgreSQL extension
pg_rrule in the form of a reusable mixin. This way, one can store and
query recurrences as specified in RFC 5545.

## Usage

1. Activate extension in PostgreSQL
```bash
$ sudo -u postgres psql <your_database>
CREATE EXTENSION pg_rrule;
```

## License

This project is licensed under the BSD-3-Clause.

(C) 2024 by Jonathan Weth <dev@jonathanweth.de>
(C) 2024 by Dominik George <dominik.george@teckids.org>
