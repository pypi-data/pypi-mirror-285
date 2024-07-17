import logging
from django.shortcuts import redirect, render
import json
import os
from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    JsonResponse,
)
from .report import (
    create_sample_json_result_file,
    read_json_result_file,
    upsert_json_result_file,
    get_html_report,
    ignore_django_axe,
)


logger = logging.getLogger(name="django_axe").setLevel(level=logging.INFO)

@ignore_django_axe
def report(request) -> HttpResponse:
    if not os.path.exists(settings.DJANGO_AXE_REPORT_PATH):
        create_sample_json_result_file(file_path=settings.DJANGO_AXE_REPORT_PATH)

    data = read_json_result_file(file_path=settings.DJANGO_AXE_REPORT_PATH)
    options = {
        "report_file_name": "report.html",
        "output_dir_path": settings.MEDIA_ROOT,
        "output_dir": "django_axe/report/",
        "rules": [],
    }
    result = get_html_report(data, options)
    return render(
        request=request, template_name="django_axe/report.html", context=result
    )


@ignore_django_axe
def reset(request) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    try:
        os.unlink(path=settings.DJANGO_AXE_REPORT_PATH)
    except Exception as e:
        logger.error(e)
    return redirect(to="django_axe:report")


def store_accessibility_report(request) -> JsonResponse:
    data = request.POST.get("result")
    url = request.POST.get("url")
    rules = request.POST.get("rules")
    data = json.loads(s=data)
    upsert_json_result_file(
        file_path=settings.DJANGO_AXE_REPORT_PATH, new_data=data, url=url, rules=rules
    )
    return JsonResponse(data=data, safe=False)
