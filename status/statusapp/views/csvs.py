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
from statusapp.models import Statusentry, Descriptor
from helpers import *

def current_results_csv(request):
    """
    Reformats the current Queryset object into a csv format.

    @rtype: HttpResponse
    @return: csv formatted current queryset
    """
    #Get the current columns from the session.
    current_columns = request.session['currentColumns']

    #Remove columns in which we don't take information from the fields.
    current_columns.remove("Hostname")
    current_columns.remove("Icons")
    current_columns.remove("Valid")
    current_columns.remove("Running")
    current_columns.remove("Hibernating")
    current_columns.remove("Named")

    #Performs the query.
    last_va = Statusentry.objects.aggregate(
            last=Max('validafter'))['last']
    statusentries = Statusentry.objects.filter(validafter=last_va).\
            extra(select={'geoip': 'geoip_lookup(address)'}).\
            order_by('nickname')

    #Gets the query options.
    query_options = {}
    if (request.GET):
        if ('resetQuery' in request.GET):
            if ('queryOptions' in request.session):
                del request.session['queryOptions']
        else:
            query_options = request.GET    
            request.session['queryOptions'] = query_options    
    if (not query_options and 'queryOptions' in request.session):
            query_options = request.session['queryOptions']

    #Use method in helper functions to filter the query results.
    statusentries = filter_statusentries(statusentries, query_options)

    #Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;\
            filename=current_results.csv'

    #Initialize dictionaries to write csv Data.
    rows = {}
    headers = {}
    
    #Make columns keys to empty lists.
    for column in current_columns: rows[column] = []

    #Populates the row dictionary with all field values.
    for entry in statusentries:
        fields_access = [("Router Name", entry.nickname),\
                ("Country Code", entry.geoip.split(',')[0][1:3]),\
                ("Bandwidth", entry.descriptorid.bandwidthobserved),\
                ("Uptime", entry.descriptorid.uptime),\
                ("IP", entry.address),\
                ("Fingerprint", entry.fingerprint),\
                ("LastDescriptorPublished", entry.published),\
                ("Contact", entry.descriptorid.rawdesc),\
                ("BadDir", entry.isbaddirectory),\
                ("DirPort", entry.dirport), ("Exit", entry.isexit),\
                ("Authority", entry.isauthority),\
                ("Fast", entry.isfast), ("Guard", entry.isguard),\
                ("V2Dir", entry.isv2dir),\
                ("Platform", entry.descriptorid.platform),\
                ("Stable", entry.isstable), ("ORPort", entry.orport),\
                ("BadExit", entry.isbadexit)]
        for k, v in fields_access:
            if k in current_columns: rows[k].append(v)

    # needed to write to the response
    writer = csv.writer(response)
    writer = csv.DictWriter(response, fieldnames=current_columns)

    #Write the headers row.
    for column in current_columns: headers[column] = column
    writer.writerow(headers)

    #Write each row in the dictionary to the csv.
    for i in range(0, len(rows[current_columns[0]])):
        dict_row = {}
        for column in current_columns:
            dict_row[column] = rows[column][i]
        writer.writerow(dict_row)

    return response


def all_ip_csv(request):
    """
    Returns a csv formatted file with all ip addresses in the Tor network.

    @rtype: HttpResponse
    @return: csv formatted list of ip addresses.
    """

    #Perform queries
    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    statusentries = Statusentry.objects.filter(validafter=last_va)
    
    #Initialize list to hold ips and populates it.
    IPs = []
    for entry in statusentries:
        IPs.append(entry.address)

    #Creates csv response type.
    response = HttpResponse(mimetype= 'text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_ips_csv'

    #Writes IP list to csv response file.
    writer = csv.writer(response)
    for ip in IPs:
        writer.writerow([ip])

    return response


def all_exit_csv(request):
    """
    Returns a csv formatted file with the exit node ip addresses
    in the Tor network.

    @rtype: HttpResponse
    @return: csv formatted list of the exit node ip addresses.
    """

    #Perform queries
    last_va = Statusentry.objects.\
            aggregate(last=Max('validafter'))['last']
    statusentries = Statusentry.objects.\
            filter(validafter=last_va, isexit=True)

    #Initilize list to hold exit node ips and populate it.
    exit_IPs = []
    for entry in statusentries:
        exit_IPs.append(entry.address)

    #Creates csv response type.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;\
            filename=all_exit_nodes.csv'

    #Writes IP list to csv response file.
    writer = csv.writer(response)
    for ip in exit_IPs:
        writer.writerow([ip])

    return response
