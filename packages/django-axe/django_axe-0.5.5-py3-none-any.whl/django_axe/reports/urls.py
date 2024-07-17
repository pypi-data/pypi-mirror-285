from django.urls import path
from django_axe.reports.views import report, reset, store_accessibility_report

app_name = "django_axe.reports"

urlpatterns = [
    path(route="store/", view=store_accessibility_report, name="store"),
    path(route="report/", view=report, name="report"),
    path(route="reset/", view=reset, name="reset"),
]
