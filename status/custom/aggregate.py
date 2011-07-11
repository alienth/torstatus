"""
Custom aggregates to count the objects in a queryset with respect to the
value of a BooleanField.
"""
from django.db import models


class SQLCountCase(models.sql.aggregates.Aggregate):
    """
    A class specifying the SQL to be performed when the CountCase
    custom aggregate class is called.
    """
    is_ordinal = True
    sql_function = 'COUNT'
    sql_template = "%(function)s(CASE %(case)s WHEN %(when)s THEN 1 ELSE null END)"

    def __init__(self, col, **extra):
        if isinstance(extra['when'], basestring):
            extra['when'] = "'%s'" % extra['when']

        if not extra.get('case', None):
            extra['case'] = '"%s"."%s"' % (extra['source'].model.\
                    _meta.db_table, extra['source'].name)

        if extra['when'] is None:
            extra['when'] = True
            extra['case'] += ' IS NULL '

        super(SQLCountCase, self).__init__(col, **extra)


class CountCase(models.Aggregate):
    """
    A custom class that counts the number of objects in a QuerySet
    with respect to the value of a given BooleanField.
    """
    name = 'COUNT'

    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = SQLCountCase(col, source=source,
                is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate
