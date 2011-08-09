"""
Custom filters for the details page.
"""
# Python-specific import statements -----------------------------------
import datetime

# Django-specific import statements -----------------------------------
from django import template
from django.db.models import Max, Count

# TorStatus-specific import statements --------------------------------
from statusapp.models import Statusentry, ActiveRelay

register = template.Library()


@register.filter
def words(seconds):
    """
    Convert a duration in seconds to a duration in words.

    >>> words('100000')
    '1 day(s), 3 hour(s), 46 minute(s), 40 second(s)'

    @type seconds: C{int}, C{float}, C{long}, C{string}, or C{buffer}
    @param seconds: The duration in seconds.
    @rtype: C{string}
    @return: The duration divided into days, hours, minutes, and
        seconds.
    """
    seconds = int(seconds)

    days = seconds / 86000
    hours = (seconds % 86000) / 3600
    minutes = (seconds % 3600) / 60
    seconds = (seconds % 60)
    return "%s day(s), %s hour(s), %s minute(s), %s second(s)" % \
            (days, hours, minutes, seconds)


@register.filter
def format_fing(fingerprint):
    """
    Format a fingerprint by capitalizing it and adding spaces every
    four characters.

    >>> format_fing('abc123def456ghi789jkl012mno345pqr678stu9')
    'ABC1 23DE F456 GHI7 89JK L012 MNO3 45PQ R678 STU9'

    @type fingerprint: C{string} or C{buffer}
    @param fingerprint: The 40-character fingerprint.
    @rtype: C{string}
    @return: The capitalized fingerprint with spaces every four
    characters.
    """
    fingerprint_list = [str(fingerprint)[i:(i + 4)] for i in
            range(0, 40, 4)]
    new_fingerprint = " ".join(fingerprint_list)

    return new_fingerprint.upper()


@register.filter
def format_family(family):
    """
    Get the family of a relay from its raw descriptor.

    It is possible that no family information for a relay exists in its
    raw descriptor. If this is the case, "No family given" is returned.

    @type family: C{string}, C{list} or C{buffer}
    @param family: The family information of a relay.
    @rtype: C{string}
    @return: The family of a relay.
    """
    if isinstance(family, list):
        family_list = family
    elif isinstance(family, str) or isinstance(family, unicode) or \
         isinstance(family, buffer):
        family_list = str(family).split(' ')
    else:
        family_list = []

    if family_list:
        links = []

        for entry in family_list:
            # Assume the entry is a fingerprint.
            if (entry[0] == "$" and len(entry[1:]) == 40):

                fingerprint = entry[1:].lower()
                poss_entries = ActiveRelay.objects.filter(
                               fingerprint=fingerprint).order_by(
                               '-validafter')

                # Fingerprints are unique, so either an entry with the
                # fingerprint is found or not. Use only the most
                # recent entry.
                if poss_entries:
                    nickname = poss_entries[0].nickname
                    links.append("<a href=\"/details/%s\">%s</a>" % \
                            (fingerprint, nickname))

                else:
                    links.append("(%s)" % entry)

            # Assume the entry is a nickname.
            else:
                poss_entries = ActiveRelay.objects.filter(
                               nickname=entry)
                poss_fingerprints = poss_entries.values(
                                    'fingerprint').annotate(
                                    Count('fingerprint'))

                # Can't find a fingerprint, so just return the
                # nickname.
                if not poss_fingerprints:
                    links.append('(%s)' % entry)

                # Found a unique fingerprint, so return the nickname
                # with a hyperlink.
                elif (len(poss_fingerprints) == 1):
                    fingerprint = poss_fingerprints[0]['fingerprint']
                    links.append("<a href=\"/details/%s\">%s</a>" % \
                                (fingerprint, entry))

                # Multiple fingerprints match the nickname. There is
                # nothing to do except return the nickname.
                else:
                    links.append("(%s)" % entry)

        return '\n'.join(links)

    return None


@register.filter
def key(d, key_name):
    """
    Return the value of a key in a dictionary.

    @type d: C{dict}
    @param d: The given dictionary.
    @type key_name: C{string}
    @param key_name: The given key.
    @rtype: C{value}
    @return: The value of the given key in the dictionary.
    """
    if key_name in d:
        return d[key_name]
