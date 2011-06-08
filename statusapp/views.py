from statusapp.models import Statusentry
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse

import os

def index(request):
	statusEntry_FullList = Statusentry.objects.filter(pk='2011-05-31 19:00:00')
	debugText = ""
	if statusEntry_FullList:
		debugText = "Everything is fine!"
		template_values = {'statusEntry_FullList': statusEntry_FullList, 'debugText': debugText}
	else:
		debugText = "Didn't get anything from the all()"
		template_values = {'debugText': debugText}
	return render_to_response('index.html', template_values)

