import csv
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import CrimeData
from .utils import convert_date
from .serializers import CrimeDataSerializer
from .filters import CrimeDataFilter

class CrimeDataUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"Status":"Failure", "Message": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith(".csv"):
            return Response({"Status":"Failure", "Message": "Only CSV files are accepted!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            crime_data_objects = []

            for row in reader:
                crime_data_objects.append(CrimeData(
                    report_number=row['DR_NO'],
                    reported_date=convert_date(row['Date Rptd']),
                    occurred_date=convert_date(row['DATE OCC']),
                    occurred_time_str=row['TIME OCC'],
                    area_code=row['AREA'],
                    area_name=row['AREA NAME'],
                    district_number=row['Rpt Dist No'],
                    crime_classification=row['Part 1-2'],
                    crime_type_code=row['Crm Cd'],
                    crime_type_name=row['Crm Cd Desc'],
                    mocodes=row['Mocodes'],
                    victim_age=row['Vict Age'],
                    victim_gender=row['Vict Sex'],
                    victim_ethnicity=row['Vict Descent'],
                    premises_code=row['Premis Cd'],
                    premises_name=row['Premis Desc'],
                    used_weapon_code=row['Weapon Used Cd'],
                    used_weapon_name=row['Weapon Desc'],
                    case_status_code=row['Status'],
                    case_status_name=row['Status Desc'],
                    other_crime_type_code_1=row['Crm Cd 1'],
                    other_crime_type_code_2=row['Crm Cd 2'],
                    other_crime_type_code_3=row['Crm Cd 3'],
                    other_crime_type_code_4=row['Crm Cd 4'],
                    location=' '.join(row['LOCATION'].split()),
                    cross_street=' '.join(row['Cross Street'].split()),
                    latitude=row['LAT'],
                    longitude=row['LON']
                ))
                print(row['DR_NO'])

            if crime_data_objects:
                CrimeData.objects.bulk_create(crime_data_objects, batch_size=5000)

            return Response({
                "Status": "Success",
                "Message": "Data Uploaded Successfully!!"
            }, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({
                "Status" :"Failure",
                "Error": str(error)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetCrimeDataView(generics.ListAPIView):
    serializer_class = CrimeDataSerializer
    queryset = CrimeData.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CrimeDataFilter


class GetCountsView(generics.ListAPIView):
    queryset = CrimeData.objects.all()
    serializer_class = CrimeDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CrimeDataFilter

    def get(self, request, *args, **kwargs):
        records = self.filter_queryset(self.get_queryset())
        grouped_counts = records.values('crime_type_name').annotate(count=Count('id'))

        counts = {item['crime_type_name']:item['count'] for item in grouped_counts}

        return Response({
            "Status": "Success",
            "Message": "Count get successfully!!",
            "Data": counts
        }, status=status.HTTP_200_OK)
