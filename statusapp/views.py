from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpRequest


import os

def index(request):
	statusEntry_FullList = Statusentry.objects.filter(pk='2011-05-31 19:00:00')
	clientAddress = request.META['REMOTE_ADDR']
	template_values = {'statusEntry_FullList': statusEntry_FullList, 'clientAddress': clientAddress}
	return render_to_response('index.html', template_values)

