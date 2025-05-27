from django.contrib import admin
from .models import CrimeData
# Register your models here.

@admin.register(CrimeData)
class CrimeDataAdmin(admin.ModelAdmin):
    list_display = ["id", "report_number", "reported_date", "occurred_date", "area_name", "crime_type_name", "case_status_name"]
    list_filter = ["occurred_date", "area_name"]
