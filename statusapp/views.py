from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse

import os

def index(request):
	statusEntry_FullList = Statusentry.objects.filter(pk='2011-05-31 19:00:00')
	descriptorDictionary = {}
	for relay in statusEntry_FullList:
		querySet = Descriptor.objects.get(descriptor="3c44166e2e872bc8348415f672db6849d5d64d50")
		descriptorDictionary[relay] = querySet
	template_values = {'statusEntry_FullList': statusEntry_FullList, 'descriptorDictionary': descriptorDictionary}
	return render_to_response('index.html', template_values)

