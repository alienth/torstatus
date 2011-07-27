"""
The module to generate the csv files for TorStatus.

There is one function for each link.
"""
# Django-specific import statements -----------------------------------
from django.http import HttpResponse
from django.db.models import Max, Sum

# CSV specific import statements
import csv

# TorStatus specific import statements --------------------------------
from statusapp.models import ActiveRelay
from helpers import *
from pages import *

NOT_MOVABLE_COLUMNS = ["Named", "Exit", "Authority", "Fast", "Guard",
                       "Hibernating", "Stable", "Running", "Valid",
                       "V2Dir", "Platform",]

def current_results_csv(request):
    """
    Reformat the current Queryset object into a csv format.

    @rtype: HttpResponse
    @return: csv formatted current queryset
    """
    current_columns = request.session['currentColumns']

    # Don't provide certain flag information in the csv
    #need to clean this up a bit
    if "Hostname" in current_columns:
        current_columns.remove("Hostname")
    if "Icons" not in current_columns:
        for flag in NOT_MOVABLE_COLUMNS:
            if flag in current_columns:
                current_columns.remove(flag)
    if "Icons" in current_columns:
        current_columns.remove("Icons")
    if "Valid" in current_columns:
        current_columns.remove("Valid")
    if "Running" in current_columns:
        current_columns.remove("Running")
    if "Named" in current_columns:
        current_columns.remove("Named")

    last_va = ActiveRelay.objects.aggregate(
              last=Max('validafter'))['last']
    active_relays = ActiveRelay.objects.filter(
                    validafter=last_va).order_by('nickname')

    #new way of filtering but it would be nice to abstract to another method
    order = ''
    basic_input = ''
    if 'search' in request.session:
        basic_input = request.session['search']
        sort_filter = ''
    elif 'sort_filter' in request.session:
        sort_filter = request.session['sort_filter']
        order, ascending_or_descending = get_order(sort_filter)

    if not order:
        order = 'nickname'
        
    if basic_input:
        active_relays = active_relays.filter(
                        Q(nickname__istartswith=basic_input) | \
                        Q(fingerprint__istartswith=basic_input) | \
                        Q(address__istartswith=basic_input)).order_by(order)
    else:
        filter_params = get_filter_params(request)
        active_relays = active_relays.filter(
                        **filter_params).order_by(order)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;\
            filename=current_results.csv'

    rows = {}
    headers = {}

    # Make columns keys to empty lists.
    for column in current_columns: rows[column] = []

    # Populates the row dictionary with all field values.
    for relay in active_relays:
        fields_access = [
                ("Router Name", relay.nickname),
                ("Country Code", relay.country),
                ("Latitude", relay.latitude),
                ("Longitude", relay.longitude),
                ("Exit Policy", relay.exitpolicy),
                ("Contact", relay.contact),
                ("Onion Key", relay.onionkey),
                ("Signing Key", relay.signingkey),
                ("Family", relay.family),
                ("Bandwidth", relay.bandwidthobserved),
                ("Uptime", relay.uptime),
                ("IP", relay.address),
                ("Fingerprint", relay.fingerprint),
                ("Last Descriptor Published", relay.published),
                ("BadDir", relay.isbaddirectory),
                ("DirPort", relay.dirport),
                ("Exit", relay.isexit),
                ("Authority", relay.isauthority),
                ("Hibernating", relay.ishibernating),
                ("Fast", relay.isfast),
                ("Guard", relay.isguard),
                ("Directory", relay.isv2dir),
                ("Platform", relay.platform),
                ("Stable", relay.isstable),
                ("ORPort", relay.orport),
                ("BadExit", relay.isbadexit)]

        for k, v in fields_access:
            if k in current_columns: rows[k].append(v)

    writer = csv.writer(response)
    writer = csv.DictWriter(response, fieldnames=current_columns)

    # Write the headers row
    for column in current_columns: headers[column] = column
    writer.writerow(headers)

    # Write each row in the dictionary to the csv
    for i in range(0, len(rows[current_columns[0]])):
        dict_row = {}
        for column in current_columns:
            dict_row[column] = rows[column][i]
        writer.writerow(dict_row)

    return response
