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
        if (line[0:6] == "accept" or line[0:6] == "reject"):
            policy.append(line)

    return "\n".join(policy)


