# Django-specific import statements -----------------------------------
from django.http import HttpResponse
from django.db.models import Max, Sum

# CSV specific import statements
import csv

# TorStatus specific import statements --------------------------------
from statusapp.models import Statusentry, Descriptor
from helpers import *

# INIT Variables ------------------------------------------------------
CURRENT_COLUMNS = ["Country Code", "Router Name", "Bandwidth",
                   "Uptime", "IP", "Hostname", "Icons", "ORPort",
                   "DirPort", "BadExit", "Named", "Exit",
                   "Authority", "Fast", "Guard", "Stable",
                   "Running", "Valid", "V2Dir", "Platform",
                   "Hibernating"]


def current_results_csv(request):

    currentColumns = []
    if not ('currentColumns' in request.session):
        currentColumns = CURRENT_COLUMNS
        currentColumns.append("Nickname")
        currentColumns.remove("Hostname")
        currentColumns.remove("Valid")
        currentColumns.remove("Running")
        currentColumns.remove("Hibernating")
        currentColumns.remove("Named")
        currentColumns.remove("Router Name")
        currentColumns.remove("Icons")
        request.session['currentColumns'] = currentColumns
    else:
        currentColumns = request.session['currentColumns']

        currentColumns.remove("Hostname")
        currentColumns.remove("Icons")
        currentColumns.remove("Valid")
        currentColumns.remove("Running")
        currentColumns.remove("Hibernating")
        currentColumns.remove("Named")
        currentColumns.remove("Router Name")
        currentColumns.append("Nickname")

    last_va = Statusentry.objects.aggregate(
            last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(validafter=last_va).extra(select={'geoip': 'geoip_lookup(address)'}).order_by('nickname')

    queryOptions = {}
    if (request.GET):
        if ('resetQuery' in request.GET):
            if ('queryOptions' in request.session):
                del request.session['queryOptions']
        else:
            queryOptions = request.GET    
            request.session['queryOptions'] = queryOptions    
    if (not queryOptions and 'queryOptions' in request.session):
            queryOptions = request.session['queryOptions']

    if queryOptions:
        if queryOptions['isauthority'] == 'yes':
            statusentries = statusentries.filter(isauthority=1)
        elif queryOptions['isauthority'] == 'no': 
            statusentries = statusentries.filter(isauthority=0)
        if queryOptions['isbaddirectory'] == 'yes':
            statusentries = statusentries.filter(isbaddirectory=1)
        elif queryOptions['isbaddirectory'] == 'no':  
            statusentries = statusentries.filter(isbaddirectory=0)
        if queryOptions['isbadexit'] == 'yes':
            statusentries = statusentries.filter(isbadexit=1)
        elif queryOptions['isbadexit'] == 'no': 
            statusentries = statusentries.filter(isbadexit=0)
        if queryOptions['isexit'] == 'yes':
            statusentries = statusentries.filter(isexit=1)
        elif queryOptions['isexit'] == 'no': 
            statusentries = statusentries.filter(isexit=0)
        '''
        if queryOptions['ishibernating'] == 'yes':
            statusentries = statusentries.filter(ishibernating=1)
        elif queryOptions['ishibernating'] == 'no': 
            statusentries = statusentries.filter(ishibernating=0)
        '''
        if queryOptions['isnamed'] == 'yes':
            statusentries = statusentries.filter(isnamed=1)
        elif queryOptions['isnamed'] == 'no': 
            statusentries = statusentries.filter(isnamed=0)
        if queryOptions['isstable'] == 'yes':
            statusentries = statusentries.filter(isstable=1)
        elif queryOptions['isstable'] == 'no': 
            statusentries = statusentries.filter(isstable=0)
        if queryOptions['isrunning'] == 'yes':
            statusentries = statusentries.filter(isrunning=1)
        elif queryOptions['isrunning'] == 'no': 
            statusentries = statusentries.filter(isrunning=0)
        if queryOptions['isvalid'] == 'yes':
            statusentries = statusentries.filter(isvalid=1)
        elif queryOptions['isvalid'] == 'no': 
            statusentries = statusentries.filter(isvalid=0)
        if queryOptions['isv2dir'] == 'yes':
            statusentries = statusentries.filter(isv2dir=1)
        elif queryOptions['isv2dir'] == 'no': 
            statusentries = statusentries.filter(isv2dir=0)
    #############################################################

    #Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=current_results.csv'

    ########################################################
    #
    #   We need to check for which columns are being searched for and
    #   get the data from each one into a dictionary.
    #
    
    rows = {}
    headers = {}
    for column in currentColumns:
        rows[column] = []

    for entry in statusentries:
        rows["Nickname"].append(entry.nickname)

    if "Country Code" in currentColumns:
        for entry in statusentries:
            rows["Country Code"].append(entry.geoip.split(',')[0][1:3])

    if "Bandwidth" in currentColumns:
        for entry in statusentries:
            rows["Bandwidth"].append(entry.descriptorid.bandwidthobserved)

    if "Uptime" in currentColumns:
        for entry in statusentries:
            rows["Uptime"].append(entry.descriptorid.uptime)

    if "IP" in currentColumns:
        for entry in statusentries:
            rows["IP"].append(entry.address)

    if "Fingerprint" in currentColumns:
        for entry in statusentries:
            rows["Fingerprint"].append(entry.fingerprint)

    if "LastDescriptorPublished" in currentColumns:
        for entry in statusentries:
            rows["LastDescriptorPublished"].append(entry.published)

    if "Contact" in currentColumns:
        for entry in statusentries:
            rows["Contact"].append(contact(entry.descriptorid.rawdesc))

    if "BadDir" in currentColumns:
        for entry in statusentries:
            rows["BadDir"].append(entry.isbaddirectory)

    if "DirPort" in currentColumns:
        for entry in statusentries:
            rows["DirPort"].append(entry.dirport)

    if "Exit" in currentColumns:
        for entry in statusentries:
            rows["Exit"].append(entry.isexit)

    if "Authority" in currentColumns:
        for entry in statusentries:
            rows["Authority"].append(entry.isauthority)

    if "Fast" in currentColumns:
        for entry in statusentries:
            rows["Fast"].append(entry.isfast)

    if "Guard" in currentColumns:
        for entry in statusentries:
            rows["Guard"].append(entry.isguard)

    if "V2Dir" in currentColumns:
        for entry in statusentries:
            rows["V2Dir"].append(entry.isv2dir)

    if "Platform" in currentColumns:
        for entry in statusentries:
            rows["Platform"].append(entry.descriptorid.platform)

    if "Stable" in currentColumns:
        for entry in statusentries:
            rows["Stable"].append(entry.isstable)

    if "ORPort" in currentColumns:
        for entry in statusentries:
            rows["ORPort"].append(entry.orport)

    if "BadExit" in currentColumns:
        for entry in statusentries:
            rows["BadExit"].append(entry.isbadexit)

    fieldnames = currentColumns
    writer = csv.writer(response)
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    for n in fieldnames:
        headers[n] = n
    writer.writerow(headers)
    for i in range(0, len(rows[currentColumns[0]])):
        dict_row = {}
        for column in currentColumns:
            dict_row[column] = rows[column][i]
        writer.writerow(dict_row)
    return response


def all_ip_csv(request):

    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    statusentries = Statusentry.objects.filter(validafter=last_va)
    
    IPs = []
    for entry in statusentries:
        IPs.append(entry.address)

    response = HttpResponse(mimetype= 'text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_ips_csv'

    writer = csv.writer(response)
    for ip in IPs:
        writer.writerow([ip])
    return response


def all_exit_csv(request):
    
    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    all_entries = Statusentry.objects.filter(validafter=last_va)
    statusentries = all_entries.filter(isexit=True)
    exit_IPs = []

    for entry in statusentries:
        exit_IPs.append(entry.address)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_exit_nodes.csv'

    writer = csv.writer(response)
    for ip in exit_IPs:
        writer.writerow([ip])

    return response
