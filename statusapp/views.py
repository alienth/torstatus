from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpRequest

def index(request):
	statusEntry_FullList = Statusentry.objects.filter(pk='2011-05-31 19:00:00')
	descriptor_list = []
	for entry in statusEntry_FullList:
		try:
			descriptor_list.append(Descriptor.objects.get(pk=entry.descriptor))
		except:
			descriptor_list.append(Descriptor())
	statusEntry_descriptorEntry = zip(statusEntry_FullList, descriptor_list)
	clientAddress = request.META['REMOTE_ADDR']
	template_values = {'statusEntry_descriptorEntry': statusEntry_descriptorEntry, 'clientAddress': clientAddress, }
	return render_to_response('index.html', template_values)

def details(request, fingerprint):
    #import datetime.datetime
    #import datetime.timedelta

    statuses = Statusentry.objects.filter(fingerprint=fingerprint)
    # This next block isn't working quite right, but it's my shot at a raw SQL 
    # query. This needs to be fixed up, see below.
    #oldest_tolerable = datetime.now() - timedelta(hours=72)
    #oldest_tol_str = str(oldest_tolerable.replace(microsecond=0))
    #recent_statuses = statuses.extra(select={'is_recent': "validafter > '" + oldest_tol_str + "'"}) 
    #recent_statuses = recent_statuses.extra(order_by = ['-is_recent'])
    #statusentry = recent_statuses.latest('validafter')

    status_count = int(statuses.count()) # int() for MySQL/PostgreSQL compatibility
    # Doesn't work -- there is no default ordering
    #recent_statuses = statuses.reverse()[max(-1, (status_count - 73)):status_count]

    recent_statuses = statuses[max(-1, (status_count - 73)):status_count]

    # This next line is extremely inefficient, but no ordering is defined so
    # there seems to be no other way... if we had experience doing raw SQL 
    # queries through django, this would be one good place to implement them.
    recent_statuses_list = list(recent_statuses)
    recent_statuses_list.reverse()

    descriptor = None
    i = 0
    while ((descriptor == None) & (i < 72)):
        try:
            descriptor = Descriptor.objects.get(descriptor=recent_statuses_list[i].descriptor)
        except:
            i += 1
    
    if (i == 72):
        i = 0

    status_and_descriptor = (recent_statuses[i], descriptor)
    template_values = {'status_and_descriptor': status_and_descriptor}
    return render_to_response('details.html', template_values)

def exitnodequery(request):
    variables = "MWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('nodequery.html', template_values)

def networkstatisticgraphs(request):
    variables = "mWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('statisticgraphs.html', template_values)
