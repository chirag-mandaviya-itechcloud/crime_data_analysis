from django.db import models

# Create your models here.

class CrimeData(models.Model):
    report_number = models.CharField(max_length=255)
    reported_date = models.DateField()
    occurred_date = models.DateField()
    occurred_time = models.TimeField(null=True, blank=True)
    occurred_time_str = models.CharField(null=True, blank=True) # need to check
    area_code = models.SmallIntegerField()
    area_name = models.CharField(max_length=255)
    district_number = models.IntegerField(default=0)
    crime_classification = models.CharField(max_length=255)
    crime_type_code = models.IntegerField(default=0)
    crime_type_name = models.CharField(max_length=255)
    mocodes = models.CharField(max_length=255, null=True, blank=True)
    victim_age = models.IntegerField(default=0)
    victim_gender = models.CharField(max_length=10, blank=True, null=True)
    victim_ethnicity = models.CharField(max_length=1, blank=True, null=True)
    premises_code = models.CharField(max_length=255, null=True, blank=True)
    premises_name = models.CharField(max_length=255, null=True, blank=True)
    used_weapon_code = models.CharField(max_length=255, null=True, blank=True)
    used_weapon_name = models.CharField(max_length=255, null=True, blank=True)
    case_status_code = models.CharField(max_length=5, null=True, blank=True)
    case_status_name = models.CharField(max_length=255,null=True, blank=True)
    other_crime_type_code_1 = models.CharField(max_length=255, null=True, blank=True)
    other_crime_name_code_1 = models.CharField(max_length=255,null=True, blank=True)
    other_crime_type_code_2 = models.CharField(max_length=255, null=True, blank=True)
    other_crime_name_code_2 = models.CharField(max_length=255, null=True, blank=True)
    other_crime_type_code_3 = models.CharField(max_length=255, null=True, blank=True)
    other_crime_name_code_3 = models.CharField(max_length=255, null=True, blank=True)
    other_crime_type_code_4 = models.CharField(max_length=255, null=True, blank=True)
    other_crime_name_code_4 = models.CharField(max_length=255, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    cross_street = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255,null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    objects = models.Manager()

    class Meta:
        db_table = 'crime_data'


class TwitterData(models.Model):
    tweet_text = models.TextField()
    tweet_sentiment = models.IntegerField(default=0, null=True, blank=True)
    tweet_date = models.DateField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'twitter_data'

class WordCloudData(models.Model):
    name = models.TextField()
    sentiment = models.FloatField(default=0, null=True, blank=True)
    weight = models.IntegerField(default=0, null=True, blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'word_cloud_data'
