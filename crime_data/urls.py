from django.urls import path
from .views import CrimeDataUploadView, GetCrimeDataView, GetCountsView, GetChartDataView, TwitterDataUploadView, UpdateDateInTweets, GetSentimentPercentage,GetWordCloudData, MakeWordCloudData

urlpatterns = [
    path('upload_crime_data', CrimeDataUploadView.as_view(), name="upload_crime_data"),
    path("get_crime_data", GetCrimeDataView.as_view(), name="get-crime-data"),
    path("get_crime_counts", GetCountsView.as_view(), name="get-crime-count"),
    path("get_chart_data", GetChartDataView.as_view(), name="get-chart-data"),
    path("upload_twitter_data", TwitterDataUploadView.as_view(), name="upload_twitter_data"),
    path("update_tweet_date", UpdateDateInTweets.as_view(), name="update-tweet-date"),
    path("get-sentiment-percentage", GetSentimentPercentage.as_view(), name="get-sentiment-percentage"),
    path("get-word-cloud", GetWordCloudData.as_view(), name="get-word-cloud"),
    path("make-word-cloud", MakeWordCloudData.as_view(), name="make-word-cloud"),
]
