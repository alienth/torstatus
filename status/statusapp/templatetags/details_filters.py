# TODO: rawdesc methods are part of the application logic, and should
# exist in statusapp.views rather than here.

from django import template

register = template.Library()

@register.filter
def words(seconds):
    """
    Convert a duration in seconds to a duration in words.
    
    @type seconds: C{int}, C{float}, C{long}, or C{string}
    @param seconds: The duration in seconds.
    @rtype: C{string}
    @return: The duration divided into days, hours, minutes, and seconds.
    """

    seconds = int(seconds)

    days = seconds/86000
    hours = (seconds % 86000)/3600
    minutes = (seconds % 3600)/60
    seconds = (seconds % 60)
    return "%s day(s), %s hour(s), %s minute(s), %s second(s)" % \
            (days, hours, minutes, seconds)

@register.filter
def format_fing(fingerprint):
    """
    Convert a fingerprint abc123def456... to a fingerprint ABC1 23DE F456...

    @type fingerprint: C{string}
    @param fingerprint: The 40-character fingerprint.
    @rtype: C{string}
    @return: The capitalized fingerprint with spaces every four characters.
    """

    fingerprint_list = [fingerprint[i:(i+4)] for i in range(0, 40, 4)]
    new_fingerprint = " ".join(fingerprint_list)    

    return new_fingerprint.upper()

@register.filter
def onion_key(rawdesc):
    """
    Get the onion key of a relay from its raw descriptor.

    @type rawdesc: C{string}
    @param rawdesc: The raw descriptor of a relay.
    @rtype: C{string}
    @return: The onion key of the relay.
    """

    # We can assume that the onion key will always be the 10-14th lines
    # in the raw descriptor, starting with line 1.
    return "\n".join(str(rawdesc).split("\n")[9:14])

@register.filter
def signing_key(rawdesc):
    """
    Get the signing key of a relay from its raw descriptor.

    @type rawdesc: C{string}
    @param rawdesc: The raw descriptor of a relay.
    @rtype: C{string}
    @return: The signing key of the relay.
    """

    # We can assume that the signing key will always be the 16-20th lines
    # in the raw descriptor, starting with line 1.
    return "\n".join(str(rawdesc).split("\n")[15:20])

@register.filter
def exitinfo(rawdesc):
    """
    Get the detailed exit policy information of a relay from its raw descriptor.

    @type rawdesc: C{string}
    @param rawdesc: The raw descriptor of a relay.
    @rtype: C{string}
    @return: The exit policy information of the relay.
    """
    policy = []
    rawdesc_array = str(rawdesc).split("\n")
    for line in rawdesc_array:
        if (line.startswith(("accept", "reject"))):
            policy.append(line)
    return policy

@register.filter
def contact(rawdesc):
    """
    Get the contact information of a relay from its raw descriptor.

    It is possible that a relay will not publish any contact information.
    In this case, "No contact information given" is returned.

    @type rawdesc: C{string}
    @param rawdesc: The raw descriptor of a relay.
    @rtype: C{string}
    @return: The contact information of the relay.
    """

    for line in str(rawdesc).split("\n"):
        if (line.startswith("contact")):
            return line[8:]
    return "No contact information given"

@register.filter
def family(rawdesc):
    #TODO: This method almost certainly belongs in statusapp.views.
    """
    Get the family of a relay from its raw descriptor.

    It is possible that no family information for a relay exists in its
    raw descriptor. If this is the case, "No family given" is returned.

    @type rawdesc: C{string}
    @param rawdesc: The raw descriptor of a relay.
    @rtype: C{string}
    @return: The family of a relay.
    """

    # Family information is given in terms of nicknames or fingerprints.
    # First, get all family information.
    fingerprints_and_nicknames = []
    for line in str(rawdesc).split("\n"):
        if (line.startswith("family")):
            fingerprints_and_nicknames = line[7:].split()

    if (len(fingerprints_and_nicknames) != 0):
        from statusapp.models import Statusentry
        from django.db.models import Max, Count
        import datetime

        links = []

        one_day = datetime.timedelta(days=1)
        last_consensus = Statusentry.objects.aggregate(last_consensus=\
                Max('validafter'))['last_consensus']
        oldest_usable = last_consensus - one_day

        for entry in fingerprints_and_nicknames:
            if (entry[0] == "$" and len(entry[1:]) == 40):
                # Assume the entry is a fingerprint.

                fingerprint = entry[1:].lower()
                poss_entries = Statusentry.objects.filter(fingerprint=\
                        fingerprint, validafter__gte=oldest_usable)\
                        .order_by('-validafter')

                # Fingerprints are unique, so either an entry with the 
                # fingerprint is found or not. Use only the most recent entry.
                if (len(poss_entries) > 0):
                    nickname = poss_entries[0].nickname
                    links.append("<a href=\"/details/%s\">%s</a>" % \
                            (fingerprint, nickname))

                else:
                    links.append("(%s)" % entry)

            else:
                # Assume the entry is a nickname.
                poss_entries = Statusentry.objects.filter(nickname=entry, \
                        validafter__gte=oldest_usable)
                poss_fingerprints = poss_entries.values('fingerprint')\
                        .annotate(Count('fingerprint'))

                if (len(poss_fingerprints) == 0):
                    # Can't find a fingerprint, so just return the nickname.
                    links.append("(%s)" % entry)
                    
                elif (len(poss_fingerprints) == 1):
                    # Found a unique fingerprint, so return the nickname with
                    # a hyperlink.
                    fingerprint = poss_fingerprints[0]['fingerprint']
                    links.append("<a href=\"/details/%s\">%s</a>" % \
                            (fingerprint, entry))
                else:
                    # Multiple nicknames match the fingerprint. There is
                    # nothing to do except returning the nickname.
                    links.append("(%s)" % entry)

        return "\n".join(links)

    return "No family given"

@register.filter
def hostname(address):
    """
    Get the hostname that corresponds to a given IP address.

    @type address: C{string}
    @param address: An IP address.
    @rtype: C{string}
    @return: The hostname that corresponds to the IP address.
    """

    from socket import getfqdn
    return getfqdn(address)
    
@register.filter
def divisible_by(counter, rows):
    """
    Returns True if rows divides counter, False otherwise.

    This method is used to divide entries (rows) in the exit policy
    information table into a given number of columns.

    @type counter: C{int}
    @param counter: The maximum number of entries (rows) per column.
    @type rows: C{int}
    @param rows: The number of rows in the table.
    @rtype: C{boolean}
    @return: True if rows divides counter, False otherwise.
    """
    return counter % rows == 0
