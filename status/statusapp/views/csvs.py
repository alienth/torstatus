# Django-specific import statements -----------------------------------
from django.http import HttpResponse
from django.db.models import Max, Sum

# CSV specific import statements
import csv

# TorStatus specific import statements --------------------------------
from statusapp.models import Statusentry, Descriptor


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
        currentColumns = ["Country Code", "Uptime", "ORPort", "DirPort",
                          "IP", "Exit", "Authority", "Fast", "Guard",
                          "Stable", "Bandwidth", "V2Dir", "Platform",
                          "BadExit", "Named"]
        request.session['currentColumns'] = currentColumns
    else:
        currentColumns = request.session['currentColumns']

        currentColumns.remove("Hostname")
        currentColumns.remove("Valid")
        currentColumns.remove("Running")
        currentColumns.remove("Hibernating")
        currentColumns.remove("Named")
        currentColumns.append("Nickname")

    last_va = Statusentry.objects.aggregate(
            last=Max('validafter'))['last']
    a = Statusentry.objects.filter(
            validafter=last_va).extra(select={
            'geoip': 'geoip_lookup(address)'})\
            .order_by('nickname')

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
            a = a.filter(isauthority=1)
        elif queryOptions['isauthority'] == 'no':
            a = a.filter(isauthority=0)
        if queryOptions['isbaddirectory'] == 'yes':
            a = a.filter(isbaddirectory=1)
        elif queryOptions['isbaddirectory'] == 'no':
            a = a.filter(isbaddirectory=0)
        if queryOptions['isbadexit'] == 'yes':
            a = a.filter(isbadexit=1)
        elif queryOptions['isbadexit'] == 'no':
            a = a.filter(isbadexit=0)
        if queryOptions['isexit'] == 'yes':
            a = a.filter(isexit=1)
        elif queryOptions['isexit'] == 'no':
            a = a.filter(isexit=0)
        '''
        if queryOptions['ishibernating'] == 'yes':
            a = a.filter(ishibernating=1)
        elif queryOptions['ishibernating'] == 'no':
            a = a.filter(ishibernating=0)
        '''
        if queryOptions['isnamed'] == 'yes':
            a = a.filter(isnamed=1)
        elif queryOptions['isnamed'] == 'no':
            a = a.filter(isnamed=0)
        if queryOptions['isstable'] == 'yes':
            a = a.filter(isstable=1)
        elif queryOptions['isstable'] == 'no':
            a = a.filter(isstable=0)
        if queryOptions['isrunning'] == 'yes':
            a = a.filter(isrunning=1)
        elif queryOptions['isrunning'] == 'no':
            a = a.filter(isrunning=0)
        if queryOptions['isvalid'] == 'yes':
            a = a.filter(isvalid=1)
        elif queryOptions['isvalid'] == 'no':
            a = a.filter(isvalid=0)
        if queryOptions['isv2dir'] == 'yes':
            a = a.filter(isv2dir=1)
        elif queryOptions['isv2dir'] == 'no':
            a = a.filter(isv2dir=0)
    #############################################################

    #Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = \
            'attachment; filename=current_results.csv'
    ########################################################
    #
    #   We need to check for which columns are being searched for and
    #   get the data from each one into a dictionary.
    #

    rows = {}
    headers = {}
    for column in currentColumns:
        rows[column] = []

    for entry in a:
        rows["Nickname"].append(entry.nickname)

    if "Country Code" in currentColumns:
        for entry in a:
            rows["Country Code"].append(entry.geoip.split(',')[0][1:3])

    if "Bandwidth" in currentColumns:
        for entry in a:
            rows["Bandwidth"].append(entry.descriptorid.bandwidthobserved)

    if "Uptime" in currentColumns:
        for entry in a:
            rows["Uptime"].append(entry.descriptorid.uptime)

    if "IP" in currentColumns:
        for entry in a:
            rows["IP"].append(entry.address)

    if "Fingerprint" in currentColumns:
        for entry in a:
            rows["Fingerprint"].append(entry.fingerprint)

    if "LastDescriptorPublished" in currentColumns:
        for entry in a:
            rows["LastDescriptorPublished"].append(entry.published)

    if "Contact" in currentColumns:
        for entry in a:
            rows["Contact"].append(_contact(entry.descriptorid.rawdesc))

    if "BadDir" in currentColumns:
        for entry in a:
            rows["BadDir"].append(entry.isbaddirectory)

    if "DirPort" in currentColumns:
        for entry in a:
            rows["DirPort"].append(entry.dirport)

    if "Exit" in currentColumns:
        for entry in a:
            rows["Exit"].append(entry.isexit)

    if "Authority" in currentColumns:
        for entry in a:
            rows["Authority"].append(entry.isauthority)

    if "Fast" in currentColumns:
        for entry in a:
            rows["Fast"].append(entry.isfast)

    if "Guard" in currentColumns:
        for entry in a:
            rows["Guard"].append(entry.isguard)

    if "V2Dir" in currentColumns:
        for entry in a:
            rows["V2Dir"].append(entry.isv2dir)

    if "Platform" in currentColumns:
        for entry in a:
            rows["Platform"].append(entry.descriptorid.platform)

    if "Stable" in currentColumns:
        for entry in a:
            rows["Stable"].append(entry.isstable)

    if "ORPort" in currentColumns:
        for entry in a:
            rows["ORPort"].append(entry.orport)

    if "BadExit" in currentColumns:
        for entry in a:
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
    a = Statusentry.objects.filter(validafter=last_va)

    IPs = []
    for entry in a:
        IPs.append(entry.address)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_ips_csv'

    writer = csv.writer(response)
    for ip in IPs:
        writer.writerow([ip])
    return response


def all_exit_csv(request):

    last_va = Statusentry.objects.aggregate(last=Max('validafter'))['last']
    all_entries = Statusentry.objects.filter(validafter=last_va)
    a = all_entries.filter(isexit=True)
    exit_IPs = []

    for entry in a:
        exit_IPs.append(entry.address)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_exit_nodes.csv'

    writer = csv.writer(response)
    for ip in exit_IPs:
        writer.writerow([ip])

    return response
