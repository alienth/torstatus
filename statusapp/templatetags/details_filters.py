from django import template

register = template.Library()

@register.filter
def words(seconds):
    "Converts a duration in seconds to a duration in words"
    days = seconds/86000
    hours = (seconds % 86000)/3600
    minutes = (seconds % 3600)/60
    seconds = (seconds % 60)
    return "%s day(s), %s hour(s), %s minute(s), %s second(s)" % \
            (days, hours, minutes, seconds)

@register.filter
def format_fing(fingerprint):
    "Converts a fingerprint abc123def456... to a fingerprint ABC1 23DE F456..."

    fingerprint_list = [fingerprint[i:(i+4)] for i in range(0, 40, 4)]
    new_fingerprint = " ".join(fingerprint_list)    

    return new_fingerprint.upper()

@register.filter
def keys(rawdesc):
    "Gets the keys from the raw descriptor, since we currently cannot get it \
            from anywhere else."

    return "\n".join(rawdesc.split("\n")[8:20])

@register.filter
def exitinfo(rawdesc):
    "Gets the detailed exit policy information from the raw descriptor"

    policy = []
    rawdesc_array = rawdesc.split("\n")
    for line in rawdesc_array:
        if (line.startswith(("accept", "reject"))):
            policy.append(line)

    return "\n".join(policy)

@register.filter
def contact(rawdesc):
    "Gets the contact information from the raw descriptor, if it exists."

    for line in rawdesc.split("\n"):
        if (line.startswith("contact")):
            return line[8:]
    return "No contact information given"

@register.filter
def family(rawdesc):
    "Returns the fingerprints of the routers defined to be in the family \
            if a family is defined in the raw descriptor"

    fingerprints_and_nicknames = []
    for line in rawdesc.split("\n"):
        if (line.startswith("family")):
            fingerprints_and_nicknames = line[7:].split()

    links = []
    if (len(fingerprints_and_nicknames) != 0):
        from statusapp.models import Statusentry
        from django.db.models import Max
        for entry in fingerprints_and_nicknames:
            if (entry[0] == "$" and len(entry[1:]) == 40):
                try:
                    fingerprint = entry[1:].lower()
                    nickname = Statusentry.objects.filter(fingerprint='%s' % fingerprint)[0].nickname
                    links.append("<a href=\"/details/%s\">%s</a>" % (fingerprint, nickname))
                except:
                    links.append("(%s)" % entry)
            else:
                try:
                    most_recent = Statusentry.objects.aggregate(last=Max('validafter'))
                    fingerprint = Statusentry.objects.get(nickname=entry, validafter=str(most_recent['last'])).fingerprint
                    links.append("<a href=\"/details/%s\">%s</a>" % (fingerprint, entry))
                except:
                    links.append("(%s)" % entry)

        return "\n".join(links)

    return "No family given"


