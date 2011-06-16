# TODO: rawdesc methods are part of the application logic, and should
# exist in statusapp.views rather than here.

from django import template

register = template.Library()

@register.filter
def words(seconds):
    """
    Convert a duration in seconds to a duration in words
    """

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
    """

    fingerprint_list = [fingerprint[i:(i+4)] for i in range(0, 40, 4)]
    new_fingerprint = " ".join(fingerprint_list)    

    return new_fingerprint.upper()

@register.filter
def onion_key(rawdesc):
    """
    Get the onion key from the raw descriptor
    """

    return "\n".join(rawdesc.split("\n")[9:14])

@register.filter
def signing_key(rawdesc):
    """
    Get the signing key from the raw descriptor
    """

    return "\n".join(rawdesc.split("\n")[15:20])

@register.filter
def exitinfo(rawdesc):
    """
    Get the detailed exit policy information from the raw descriptor
    """

    policy = []
    rawdesc_array = rawdesc.split("\n")
    for line in rawdesc_array:
        if (line.startswith(("accept", "reject"))):
            policy.append(line)

    return "\n".join(policy)

@register.filter
def contact(rawdesc):
    """
    Get the contact information from the raw descriptor, if it exists
    """

    for line in rawdesc.split("\n"):
        if (line.startswith("contact")):
            return line[8:]
    return "No contact information given"

@register.filter
def family(rawdesc):
    """
    Return the fingerprints of the routers defined to be in the family
    if a family is defined in the raw descriptor
    """

    fingerprints_and_nicknames = []
    for line in rawdesc.split("\n"):
        if (line.startswith("family")):
            fingerprints_and_nicknames = line[7:].split()

    if (len(fingerprints_and_nicknames) != 0):
        links = []
        from statusapp.models import Statusentry
        from django.db.models import Max
        import datetime
        for entry in fingerprints_and_nicknames:
            if (entry[0] == "$" and len(entry[1:]) == 40):
                try:
                    fingerprint = entry[1:].lower()
                    nickname = Statusentry.objects.filter(fingerprint='%s' % \
                            fingerprint)[0].nickname
                    links.append("<a href=\"/details/%s\">%s</a>" % \
                            (fingerprint, nickname))
                except:
                    links.append("(%s)" % entry)
            else:
                try:
                    most_recent = Statusentry.objects.aggregate(last=\
                            Max('validafter'))
                    fingerprint = ""
                    hours_back = 0
                    while (fingerprint == "" and hours_back < 25):
                        try:
                            fingerprint = Statusentry.objects.get(nickname=\
                                    entry, validafter=str(most_recent['last'] \
                                    - datetime.timedelta(hours=\
                                    hours_back))).fingerprint
                        except:
                            hours_back += 1
                    if (fingerprint == ""):
                        links.append("(%s)" % entry)
                    else:
                        links.append("<a href=\"/details/%s\">%s</a>" \
                                % (fingerprint, entry))
                except:
                    links.append("(%s)" % entry)

        return "\n".join(links)

    return "No family given"

@register.filter
def hostname(address):
    """
    Get the hostname that corresponds to a given IP address
    """

    from socket import getfqdn
    return getfqdn(address)
