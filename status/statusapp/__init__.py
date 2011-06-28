"""
A custom typecast for psycopg2.

Psycopg2, by default,
casts a BIGINT[] in PostgreSQL to a python list, removing the indices
given, e.g. [86:86]={2563637}. These are necessary, however, to gather
96 data points consisting of (date, bandwidth) pairs for use in
bandwidth history graphs.

@see: http://www.initd.org/psycopg/docs/advanced.html
    #type-casting-from-sql-to-python
"""
import psycopg2


def __none_to_zero(string):
    """
    Return '0' if the string is "none" or "null";
    return the string itself otherwise.

    @type string: C{string}
    @param string: The string to test for values of "none" or "null".
    @rtype: C{string}
    @return: '0' if the string is "none" or "null", the string itself
        otherwise.
    """

    if (string.lower() == "none" or string.lower() == "null"):
        return '0'
    else:
        return string


def cast_array(value, cur):
    """
    Return the PostgreSQL array as a tuple consising of the starting
    index, ending index, and the array itself (as a python list).

    >>> cast_array([13:15]={2526642,7003442,6466167},
            psycopg2.connection.cursor())
    (13, 15, [2526642, 7003442, 6466167])

    @type value: C{string}
    @param value: The PostgreSQL as a string, exactly as it appears in
        queries.
    @type cur: C{psycopg2.cursor}
    @param cur: The psycopg2 cursor object.
    @rtype: C{tuple} of C{int}, C{int}, and C{list} of C{int}
    @return: A tuple consisting of the starting index, ending index,
        and the PostgreSQL array itself (as a python list of bandwidth
        values)
    """
    if value is None:
        return None

    value = str(value)
    indices, arraystr = value.split('=')

    startstr, endstr = indices.strip('[]').split(':')
    start = int(startstr)
    end = int(endstr)

    # Make all 'null' or 'none' entries '0', then convert the entries
    # in the array to integers
    array = map(lambda x: int(__none_to_zero(x)),
            arraystr.strip('{}').split(','))
    return (start, end, array)


# 1016 is the psycopg2 object ID (OID) for BIGINT[] fields. See
# http://www.initd.org/psycopg/docs/advanced.html#
# type-casting-from-sql-to-python to see how this was determined.
ARRAY = psycopg2.extensions.new_type((1016,), "BIGINT[]", cast_array)
psycopg2.extensions.register_type(ARRAY)
