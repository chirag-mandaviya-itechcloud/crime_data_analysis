from django.urls import path
from .views import CrimeDataUploadView, GetCrimeDataView, GetCountsView

urlpatterns = [
    path('upload_crime_data', CrimeDataUploadView.as_view(), name="upload_crime_data"),
    path("get_crime_data", GetCrimeDataView.as_view(), name="get-crime-data"),
    path("get_crime_counts", GetCountsView.as_view(), name="get-crime-count"),
]
