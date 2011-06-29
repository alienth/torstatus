# Django-specific import statements -----------------------------------
from django.http import HttpResponse
from django.db.models import Max, Sum

# CSV specific import statements
import csv

# TorStatus specific import statements --------------------------------
from statusapp.models import Statusentry, Descriptor


def current_results_csv(request):

    current_columns = request.session['currentColumns']

    current_columns.remove("Hostname")
    current_columns.remove("Icons")
    current_columns.remove("Valid")
    current_columns.remove("Running")
    current_columns.remove("Hibernating")
    current_columns.remove("Named")

    last_va = Statusentry.objects.aggregate(
            last=Max('validafter'))['last']

    statusentries = Statusentry.objects.filter(validafter=last_va).\
            extra(select={'geoip': 'geoip_lookup(address)'}).order_by('nickname')

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


    #Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=current_results.csv'

    #   We need to check for which columns are being searched for and
    #   get the data from each one into a dictionary.
    
    rows = {}
    headers = {}
    
    for column in current_columns: rows[column] = []

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

    writer = csv.writer(response)
    writer = csv.DictWriter(response, fieldnames=current_columns)

    for column in current_columns: headers[column] = column

    writer.writerow(headers)

    for i in range(0, len(rows[current_columns[0]])):
        dict_row = {}
        for column in current_columns:
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
    statusentries = Statusentry.objects.filter(validafter=last_va, isexit=True)
    exit_IPs = []

    for entry in statusentries:
        exit_IPs.append(entry.address)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_exit_nodes.csv'

    writer = csv.writer(response)
    for ip in exit_IPs:
        writer.writerow([ip])

    return response
