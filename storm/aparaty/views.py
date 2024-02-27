import datetime
import os
import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Aparat

logger = logging.getLogger(__name__)

@login_required
def kom_aparaty(request):
    aparaty = Aparat.objects.all()
    context = {}
    context['aparaty'] = aparaty
    return render(request, 'aparaty/kom_aparaty.html', context)
