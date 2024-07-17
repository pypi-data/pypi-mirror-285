from django.urls import path
from django_axe.reports.views import report, reset, store

app_name = "django_axe.reports"

urlpatterns = [
    path(route="store/", view=store, name="store"),
    path(route="report/", view=report, name="report"),
    path(route="reset/", view=reset, name="reset"),
]
