from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render

from . import utils


def index(request):
    """The view for the index page"""
    return render(request, "app/index.html")


def questionnaire(request):
    """The view for the questionnaire page"""
    if request.method != 'POST':
        response = HttpResponseNotAllowed(['POST'])
        response.content = """
        <h1>Cette URL n'est pas accessible directement</h1>
        <p><i>Veuillez remplir le formulaire de la page d'accueil</i></p>"""
        return response

    # We get the datas of the form on index page
    title = request.POST.get("title")
    nb = int(request.POST.get("recommendationsNumber"))
    age = request.POST.get("age")

    # We generate recommendations
    df_recommendations = utils.generate_recommendations(title, nb, age)

    # We store in the session the title, the number of movies to recommend and the indexes of the recommendations
    request.session["title"] = title
    request.session["nb"] = nb
    request.session["recommendations_idx"] = df_recommendations.index.tolist()

    # We get the languages and the genres of the movies in df_recommendations
    languages = df_recommendations["language"].unique().tolist()
    genres = df_recommendations["genres"].apply(lambda x: (x.split("|"))).explode().unique().tolist()

    # We put group_size elements on each row
    group_size = 7
    languages = [languages[i:i + group_size] for i in range(0, len(languages), group_size)]
    genres = [genres[i:i + group_size] for i in range(0, len(genres), group_size)]

    # We get the actor_1_name and the director_name in df_recommendations
    actors = df_recommendations.loc[df_recommendations["actor_1_name"] != "", "actor_1_name"].unique().tolist()
    directors = df_recommendations.loc[df_recommendations["director_name"] != "", "director_name"].unique().tolist()

    # We store all datas we need in the template in a dict
    context = {"languages": languages,
               "genres": genres,
               "actors": actors,
               "directors": directors,
               "title": title,
               "nb": nb}

    # And we return the render of the template
    return render(request, "app/questionnaire.html", context=context)


def result(request):
    """The view for the result page"""
    if request.method != 'POST':
        response = HttpResponseNotAllowed(['POST'])
        response.content = """
        <h1>Cette URL n'est pas accessible directement</h1>
        <p><i>Veuillez remplir le formulaire de la page d'accueil</i></p>"""
        return response

    # We get the choices in the form in 'data'
    data = request.POST

    # We get title, number of recommendations and index of recommended movies from the session
    title = request.session.get("title")
    nb = request.session.get("nb")
    idx = request.session.get("recommendations_idx")

    # We load recommendations with the indexes
    df = utils.load_recommendations(idx)

    # We store all the choices in a dict
    choices = {"age": data.get("age"),
               "languages": data.getlist("languages"),
               "duration": data.getlist("duration"),
               "filter": data.get("filter"),
               "genres": data.getlist("genres"),
               "actors": data.getlist("actors"),
               "directors": data.getlist("directors")}

    # We filter recommendations with the user choices
    df = utils.filter_recommendations(df, choices, nb)

    # We get the Series we need to use in the template
    titles = df["movie_title"]
    urls = df["movie_imdb_link"]
    genres = df["genres"]
    actors = df["actor_1_name"]
    directors = df["director_name"]

    # We store all in a list of dict contains datas for each movie
    recommended_films = [{"title": title,
                          "url": url,
                          "thumbnail_url": utils.get_thumbnail_url(url),
                          "genres": ", ".join(genre.split("|")),
                          "actor": actor,
                          "director": director} for title, url, genre, actor, director in zip(titles,
                                                                                              urls,
                                                                                              genres,
                                                                                              actors,
                                                                                              directors)]

    # We store all datas we need in the template in a dict
    context = {"title": title,
               "nb": nb,
               "recommended_films": recommended_films}

    # And we return the render of the template
    return render(request, "app/result.html", context)


def get_movie_titles(request):
    """The API view to get movies title with AJAX for autocomplete"""
    # We load movies dataframe
    df = utils.load_movies()
    # We store the movies titles filtered by age in a dict
    titles = {"adult": sorted(utils.filter_by_age_category(df=df, age_category="adult")["movie_title"].tolist()),
              "teenager": sorted(utils.filter_by_age_category(df=df, age_category="teenager")["movie_title"].tolist()),
              "child": sorted(utils.filter_by_age_category(df=df, age_category="child")["movie_title"].tolist())}
    # And we return a JsonResponse contains this dict
    return JsonResponse(titles)
