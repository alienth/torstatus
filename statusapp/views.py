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
    statusEntry_FullList = Statusentry.objects.filter(pk='2011-05-31 19:00:00')
    #descriptor = Descriptor.objects.get(pk=fingerprint)
    template_values = {'fingerprint': fingerprint,}
    
    return render_to_response('details.html', template_values)

def exitnodequery(request):
    variables = "MWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('nodequery.html', template_values)

def networkstatisticgraphs(request):
    variables = "mWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('statisticgraphs.html', template_values)
