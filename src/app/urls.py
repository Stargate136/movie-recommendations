from django.urls import path


from .views import index, questionnaire, result, get_movie_titles

app_name = "app"

urlpatterns = [
    path("", index, name="index"),
    path("questionnaire/", questionnaire, name="questionnaire"),
    path("result/", result, name="result"),
    path("get-titles/", get_movie_titles, name="get_movie_titles")
]
