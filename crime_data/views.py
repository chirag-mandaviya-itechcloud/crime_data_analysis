import csv
import io
import logging
import numpy as np
import nltk
import spacy
from nltk.corpus import stopwords
from sklearn.cluster import DBSCAN
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from collections import defaultdict, Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import numpy as np


from .models import CrimeData, TwitterData, WordCloudData
from .utils import convert_date, get_center, generate_date, round_percent_dict_to_100
from .serializers import CrimeDataSerializer, TwitterDataSerializer, WordCloudDataSerializer
from .filters import CrimeDataFilter,TwitterDataFilter

# nltk.download('stopwords')

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
                # print(row['DR_NO'])

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
        grouped_counts = records.values('crime_type_name').annotate(count=Count('id')).order_by('-count')

        # Step 2: Convert to NumPy array
        coordinates = np.array(
            [
                [float(record.latitude), float(record.longitude)] for record in records if record.latitude and record.longitude
            ]
        )

        db = DBSCAN(eps=0.01, min_samples=1).fit(coordinates)
        labels = db.labels_

        hotspots = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:
                continue
            cluster_points = coordinates[labels == label]
            center = cluster_points.mean(axis=0)
            hotspots.append({
                "latitude": round(center[0], 6),
                "longitude": round(center[1], 6),
                "count": len(cluster_points)
            })

            # Sort hotspots by count descending
            hotspots.sort(key=lambda x: x['count'], reverse=True)

            center = get_center([[h.get("latitude"), h.get("longitude")] for h in hotspots])

        return Response({
            "Status": "Success",
            "Message": "Count get successfully!!",
            "Data": {
                "counts": grouped_counts,
                "map_data": {
                    "center": {"lat":center.get("latitude"), "lng": center.get("longitude")},
                    "hotspots": hotspots
                },
                "recent": self.get_serializer(records.order_by('-reported_date'), many=True).data  # for three results
            }
        }, status=status.HTTP_200_OK)


class GetChartDataView(generics.ListAPIView):
    queryset = CrimeData.objects.all()
    serializer_class = CrimeDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CrimeDataFilter

    def get(self, request, *args, **kwargs):
        records = self.filter_queryset(self.get_queryset())
        date_wise_counts = records.values('reported_date').annotate(count=Count('id'))
        crime_wise_counts = records.values('crime_type_name').annotate(count=Count('id'))

        return Response({
            "Status": "Success",
            "Message": "Data get successfully!!",
            "Data": {
                "lineChartData": date_wise_counts,
                "barChartData": crime_wise_counts
            }
        }, status=status.HTTP_200_OK)


class TwitterDataUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"Status":"Failure", "Message": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith(".csv"):
            return Response({"Status":"Failure", "Message": "Only CSV files are accepted!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file, newline='')
            reader = csv.DictReader(io_string)
            twitter_data_objects = []

            for row in reader:
                if row['clean_text']:
                    twitter_data_objects.append(TwitterData(
                        tweet_text=row.get('clean_text'),
                        tweet_sentiment=int(row.get('category')) if row.get('category') is not None else 0
                    ))
                    print(row['category'])

            if twitter_data_objects:
                TwitterData.objects.all().delete()
                TwitterData.objects.bulk_create(twitter_data_objects, batch_size=5000)

            return Response({
                "Status": "Success",
                "Message": "Data Uploaded Successfully!!"
            }, status=status.HTTP_200_OK)

        except Exception as error:
            return Response({
                "Status" :"Failure",
                "Error": str(error)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSentimentPercentage(generics.ListAPIView):
    queryset = TwitterData.objects.all()
    serializer_class = TwitterDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TwitterDataFilter

    def get(self, request, *args, **kwargs):
        records = self.filter_queryset(self.get_queryset())

        counts = records.values('tweet_sentiment').annotate(count=Count('id'))
        date_wise_counts = records.values("tweet_date", "tweet_sentiment").annotate(count=Count("id")).order_by("tweet_date")

        sentiment_map = {
            1: 'positive',
            0: 'neutral',
            -1: 'negative',
        }
        result = {"positive": 0, "neutral": 0, "negative": 0}

        # compute percentage overall
        for item in counts:
            label = sentiment_map.get(item['tweet_sentiment'], "unknown")
            result[label] = round((item['count'] / len(records)) * 100, 2)

        result = round_percent_dict_to_100(result)

        date_wise_data = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0, "total": 0})

        for row in date_wise_counts:
            date = row["tweet_date"]
            label = sentiment_map.get(row["tweet_sentiment"])
            count = row["count"]

            date_wise_data[date][label] += count
            date_wise_data[date]["total"] += count

        # compute percentage
        results = []
        for date, data in sorted(date_wise_data.items()):
            total = data["total"]
            one_result = {
                "positive": round((data["positive"] / total) * 100, 2),
                "neutral": round((data["neutral"] / total) * 100, 2),
                "negative": round((data["negative"] / total) * 100, 2)
            }
            one_result = round_percent_dict_to_100(one_result)
            one_result["date"] = date
            results.append(one_result)
        return Response({
            "status": "Success",
            "overview": result,
            "timeline": results,
        }, status=status.HTTP_200_OK)


class UpdateDateInTweets(APIView):
    def post(self, request):
        twitter_data = TwitterData.objects.all()

        for tweet in twitter_data:
            tweet.tweet_date = generate_date()

        TwitterData.objects.bulk_update(twitter_data, ['tweet_date'])

        return Response({
            "status": "Success", "detail": "Date Added!!"
        }, status=status.HTTP_200_OK)


class MakeWordCloudData(APIView):
    def get(self, request):
        logger = logging.getLogger("crime_analyzer_logger")
        records = TwitterData.objects.all()


        # Add words in one list
        # words = []
        # for tweet in records:
        #     words += tweet.tweet_text.split()

        # counts = Counter(words)

        # # Ignore common stopwords (you can use nltk.corpus.stopwords instead)
        # stpwords = stopwords.words('english')
        # stpwords.extend(["like", "one", "people", "even", "time", "also", "years", "dont"])
        # keywords = [word for word in counts.items() if word[0] not in stpwords]

        # sorted_keywords = sorted(keywords, key=lambda x: x[1], reverse=True)

        # result = []
        # for i, (word, freq) in enumerate(sorted_keywords[:21]):
        #     result.append({
        #         "id": i + 1,
        #         "name": word.title(),
        #         "weight": freq,  # Scale weight
        #         "sentiment": round(TextBlob(word).sentiment.polarity, 2)
        #         # "sentiment": analyzer.polarity_scores(word)["compound"]
        #     })


        # ----------------------------------------------------------------
        # ----------------------------------------------------------------

        categories = ["Public Safety", "Police Response", "Community Outreach", "Traffic Violations", "Drug Activity",
              "Property Crime", "Youth Programs", "Emergency Services", "Homelessness", "Street Lighting",
              "Noise Complaints", "Community Events", "School Safety", "Parking Issues", "Theft" ]

        # Initialize the zero-shot classifier
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

        category_stats = defaultdict(lambda: {'count': 0, 'sentiment_sum': 0})
        tweet_texts = list(records.values_list('tweet_text', flat=True))

        for index, text in enumerate(tweet_texts[:20001], start=1):
            # Get best-matching category
            result = classifier(text, categories)
            best_category = result['labels'][0]

            # Get sentiment
            sentiment = TextBlob(text).sentiment.polarity  # -1 to +1

            # Aggregate
            category_stats[best_category]['count'] += 1
            category_stats[best_category]['sentiment_sum'] += sentiment
            logger.info(f"{index}: {text}")
            # print(f"{index}: {text}")

        final_summary = []

        for idx, (category, stats) in enumerate(category_stats.items(), start=1):
            count = stats['count']
            avg_sentiment = stats['sentiment_sum'] / count if count > 0 else 0
            final_summary.append(WordCloudData(
                weight=count,
                sentiment=round(avg_sentiment, 3),
                name=category,
            ))

        WordCloudData.objects.bulk_create(final_summary, batch_size=20)

        return Response({
            "status": "Success",
            "topics": "Topics Stored Successfully"
        }, status=status.HTTP_200_OK)


class GetWordCloudData(generics.ListAPIView):
    queryset = WordCloudData.objects.all()
    serializer_class = WordCloudDataSerializer

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        return Response({
            "status":"Success",
            "topics": res.data
        }, status=status.HTTP_200_OK)
