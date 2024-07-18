from django_axe.reports.report import (
    ignore_django_axe,
)

import logging
from django.shortcuts import render
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    JsonResponse,
)
from django_axe.reports import views

logger = logging.getLogger(name="django_axe").setLevel(level=logging.INFO)

def home(request):
    return render(request=request, template_name="base.html")

@ignore_django_axe
def report(request) -> HttpResponse:
    return views.report(request=request)


@ignore_django_axe
def reset(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    return views.reset(request=request)


def store(request) -> JsonResponse:
    return views.store(request=request)
