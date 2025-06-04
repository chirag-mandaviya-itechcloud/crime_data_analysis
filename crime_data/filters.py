import django_filters
from .models import CrimeData, TwitterData

CRIME_TYPES = {
  "theft": [
    "THEFT FROM MOTOR VEHICLE - PETTY ($950 & UNDER)",
    "THEFT-GRAND ($950.01 & OVER)EXCPT,GUNS,FOWL,LIVESTK,PROD",
    "THEFT PLAIN - PETTY ($950 & UNDER)",
    "EMBEZZLEMENT, GRAND THEFT ($950.01 & OVER)"
  ],
  "vehicle": [
    "VEHICLE - STOLEN",
    "VEHICLE - ATTEMPT STOLEN",
    "VEHICLE, STOLEN - OTHER (MOTORIZED SCOOTERS, BIKES, ETC)",
  ],
  "violence": [
    "ROBBERY",
    "ASSAULT WITH DEADLY WEAPON, AGGRAVATED ASSAULT",
    "BATTERY - SIMPLE ASSAULT"
  ],
  "sexual": [
    "RAPE, ATTEMPTED",
    "RAPE, FORCIBLE",
    "INDECENT EXPOSURE",
    "SEX,UNLAWFUL(INC MUTUAL CONSENT, PENETRATION W/ FRGN OBJ",
    "BATTERY WITH SEXUAL CONTACT"
  ],
  "child": [
    "CHILD NEGLECT (SEE 300 W.I.C.)",
    "CRM AGNST CHLD (13 OR UNDER) (14-15 & SUSP 10 YRS OLDER)",
    "CHILD PORNOGRAPHY"
  ],
  "vandalism": [
    "VANDALISM - FELONY ($400 & OVER, ALL CHURCH VANDALISMS)",
    "VANDALISM - MISDEAMEANOR ($399 OR UNDER)",
    "TRESPASSING",
  ],
    "burglary": [
        "BURGLARY",
        "BURGLARY FROM VEHICLE"
    ],
  "threats": [
    "CRIMINAL THREATS - NO WEAPON DISPLAYED"
  ],
  "fraud": [
    "EXTORTION",
    "EMBEZZLEMENT, GRAND THEFT ($950.01 & OVER)"
  ],
  "assault": [
      "ASSAULT WITH DEADLY WEAPON, AGGRAVATED ASSAULT",
    "BATTERY - SIMPLE ASSAULT"
  ],
  "other": [
    "OTHER MISCELLANEOUS CRIME"
  ]
}


class CrimeDataFilter(django_filters.FilterSet):
    area_name = django_filters.CharFilter()
    crime_type_name = django_filters.CharFilter(method="filter_by_crime_type_name")
    reported_date = django_filters.DateTimeFromToRangeFilter()
    source = django_filters.CharFilter(method="filter_by_source")

    class Meta:
        model = CrimeData
        fields = ['area_name', 'crime_type_name', 'reported_date', 'source']

    def filter_by_crime_type_name(self, queryset, name, value):
        if value == "all":
            return queryset
        crime_types = CRIME_TYPES.get(value)
        if crime_types:
            return queryset.filter(crime_type_name__in=crime_types)
        return queryset.none()

    def filter_by_source(self, queryset, name, value):
        if value == "all":
            return queryset
        return queryset.filter(source=value)



class TwitterDataFilter(django_filters.FilterSet):
    tweet_date = django_filters.DateTimeFromToRangeFilter()
    tweet_sentiment = django_filters.NumberFilter()

    class Meta:
        model = TwitterData
        fields = ['tweet_date', 'tweet_sentiment']
