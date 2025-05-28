import django_filters
from .models import CrimeData

class CrimeDataFilter(django_filters.FilterSet):
    area_name = django_filters.CharFilter()
    crime_type_name = django_filters.CharFilter()
    reported_date = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = CrimeData
        fields = ['area_name', 'crime_type_name', 'reported_date']
