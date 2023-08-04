import pandas as pd
import requests
from bs4 import BeautifulSoup

from project import settings
from sklearn.neighbors import NearestNeighbors


DATA_DIR = settings.BASE_DIR / "data"


def load_movies():
    """Function to load movies dataframe

    Returns:
        pd.DataFrame: A dataframe contains all movies
    """
    # We load the dataframe from CSV file
    df = pd.read_csv(DATA_DIR / "cleaned_data.csv")

    # We fill empty values with an empty string ( Don't worry the dataframe is already cleaned ! )
    df.fillna("", inplace=True)
    return df


def load_recommendations(idx):
    """Function to load recommendations

    Args:
        idx (iterable): An iterable contains indexes of movies to load

    Returns:
        pd.DataFrame: A dataframe contains movies at the indexes in idx
    """
    # We load the movies dataframe
    df = load_movies()

    # We return only the movies with an index in 'idx'
    return df.iloc[idx]


def filter_by_age_category(df, age_category):
    """Function to filter the movies dataframe by age_category

    Args:
        df (pd.DataFrame): A movies dataframe
        age_category (str): The age category to filter (possibles values : ["adult", "teenager", "child"])

    Returns:
        pd.Dataframe: The dataframe after filtering
    """
    if age_category == "adult":
        return df
    elif age_category == "teenager":
        return df[df["age_category"] != "adult"]
    elif age_category == "child":
        return df[df["age_category"].isin(["child", "unknown"])]


def score(movie, df_recommendations):
    """Function to score the model

    Args:
        movie (pd.DataFrame): A dataframe of the movie selected by the user ( 1 row )
        df_recommendations (pd.DataFrame): A dataframe containing the recommendations

    Returns:
        float: The score of the recommendations
    """
    genres = movie["genres"].str.split("|")
    actors = movie[["actor_1_name", "actor_2_name", "actor_3_name"]]
    director = movie["director_name"].values[0]

    score = 0
    for i, row in df_recommendations.iterrows():
        genres_recommendation = row["genres"].split("|")
        for j, genre in enumerate(genres_recommendation):
            try:
                if genre in genres:
                    score += 1 / j
            except KeyError:
                pass
        if row["actor_1_name"] in actors:
            score += 1
        if row["actor_2_name"] in actors:
            score += 1
        if row["actor_3_name"] in actors:
            score += 1
        if row["director_name"] == director:
            score += 1
    return score


def generate_recommendations(title="", nb=5, age_category="adult"):
    """Function to generate recommendations using Machine Learning

    Args:
        title (str, optional): The title of the movie the user chosen. Defaults to "".
        nb (int, optional): Number of recommandations the user want. Defaults to 5.
        age_category (str, optional): A string representing the category of age.
                                      Possibles values : ["child", "teenager", "adult"]. Defaults to "adult".

    Returns:
        pd.DataFrame: A dataframe contains movies are recommended by the Machine Learning algorithm
    """
    # we load the preprocessed and the movies dataframe
    df_ML = pd.read_csv(DATA_DIR / "preprocessed_data.csv.gz")
    df_movies = load_movies()

    # We filter ML dataframe by age
    df_ML = df_ML[df_ML.index.isin(filter_by_age_category(df_movies, age_category).index)]

    # We rename the first column to idx
    new_columns = df_ML.columns.tolist()
    new_columns[0] = 'idx'
    df_ML.columns = new_columns

    # We fit the NearestNeighbors model

    # BESTS HYPERPARAMETERS
    # {'algorithm': 'auto', 'leaf_size': 10, 'metric': 'manhattan', 'p': 1}
    nn = NearestNeighbors(n_neighbors=nb * 10 + 1, algorithm="auto", leaf_size=10, metric="manhattan", p=1)
    nn.fit(df_ML.drop("idx", axis=1))

    # We get the index of the movie with his title, and we get the neighbors
    idx = df_movies[df_movies["movie_title"] == title].index[0]
    distances, indices = nn.kneighbors(df_ML[df_ML["idx"] == idx].drop("idx", axis=1))

    # We get the indexes of the movies (except the first, it's the input movie)
    indices = df_ML.iloc[indices[0, 1:]]["idx"].values

    # And we load the recommendations in a dataframe
    df_recommendations = load_recommendations(indices)

    # We count the score ( genre1 +1, genre2+0.5, actor+1, director+1 )
    movie = df_movies[df_movies["movie_title"] == title]
    print("score :", score(movie, df_recommendations))

    return df_recommendations


def filter_recommendations(df, choices, nb=5):
    """Function to filter recommandations by user choices

    Args:
        df (pd.DataFrame): A dataframe contains movies recommendations
        choices (dict): A dictionary containing the user choices
        nb (int, optional): The number of recommendations needed. Defaults to 5.

    Returns:
        pd.DataFrame: A dataframe contains the movies recommendations filtered
    """
    # Filter by languages
    languages = choices["languages"]
    if languages:
        df = df[df["language"].isin(languages)]

    # Filter by time
    durations = choices["duration"]
    if durations:
        temp_df = None
        if "0" in durations:
            mask = df["duration"] < 90
            temp_df = pd.concat([temp_df, df[mask]])
        if "1" in durations:
            mask_1 = df["duration"] >= 90
            mask_2 = df["duration"] < 120
            temp_df = pd.concat([temp_df, df[mask_1 & mask_2]])
        if "2" in durations:
            mask_1 = df["duration"] >= 120
            mask_2 = df["duration"] < 180
            temp_df = pd.concat([temp_df, df[mask_1 & mask_2]])
        if "3" in durations:
            mask = df["duration"] >= 180
            temp_df = pd.concat([temp_df, df[mask]])

        if len(temp_df):
            df = temp_df

    # Sort selection criteria
    filter_choice = choices["filter"]

    # Sort by gender in choices
    if filter_choice == "genres":
        def sort_func(title_genres, choice_genres):
            return title_genres.apply(lambda x: sum(1 for genre in x.split("|") if genre in choice_genres))
        genres = choices["genres"]
        if genres:
            df = df.sort_values(by="genres",
                                key=lambda x: sort_func(x, genres),
                                ascending=False)

    # Sort by actors in choices
    elif filter_choice == "actors":
        def sort_func(title_actors, choice_actors):
            return title_actors.apply(lambda x: 1 if x in choice_actors else 0)
        actors = choices["actors"]
        if actors:
            df = df.sort_values(by="actor_1_name",
                                key=lambda x: sort_func(x, actors),
                                ascending=False)

    # Sort by director in choices
    elif filter_choice == "directors":
        def sort_func(title_director, choice_directors):
            return title_director.apply(lambda x: 1 if x in choice_directors else 0)
        directors = choices["directors"]
        if directors:
            df = df.sort_values(by="director_name",
                                key=lambda x: sort_func(x, directors),
                                ascending=False)

    return df.iloc[:nb, :]


def get_thumbnail_url(url):
    """Function to scrap IMDB website and get the movie image URL

    Args:
        url (str): The url of the movie

    Returns:
        str: The url of the movie image 
    """
    # We modify url to get the photo gallery webpage
    url = "/".join(url.split("/")[:-1]) + "/mediaindex?ref_=tt_ov_mi_sm"

    response = requests.get(url)                        # We get the HTML response of the url
    soup = BeautifulSoup(response.text, "html.parser")  # We parse HTML in a BeautifulSoup object
    img = soup.find("img")                              # We get the first image of the webpage
    img_url = img.get("src")                            # We get the source of the image
    return img_url                                      # And we return it


def cross_validation():
    """Function to do a cross validation on the KNN
       and write the result in a files in the cross_validation_logs directory

        Args:
            url (str): The url of the movie

        Returns:
            str: The url of the movie image
        """
    # This module is for beeping ( to ear when scoring is finish )
    import winsound
    from project.settings import BASE_DIR

    LOG_DIR = BASE_DIR / "cross_validation_logs"
    LOG_DIR.mkdir(exist_ok=True)

    df_ML = pd.read_csv(DATA_DIR / "preprocessed_data.csv.gz")
    df_movies = load_movies()

    total_counter = 0

    def best_score(fitted_knn, total_counter):

        # We count the score ( genre1 +1, genre2+0.5, actor+1, director+1 )
        max_score = 0
        for i, row in df_ML.iterrows():
            # Prédiction des indices et distances pour les 3 plus proches voisins
            _, indices = fitted_knn.kneighbors(row.values.reshape(1, -1))

            df_recommendations = load_recommendations(indices[0]).iloc[1:]

            genres = df_movies.iloc[i]["genres"].split("|")
            score = 0

            for j, row_reco in df_recommendations.iterrows():
                genres_recommendation = row_reco["genres"].split("|")
                for k, genre in enumerate(genres_recommendation, 1):
                    try:
                        if genre in genres:
                            score += 1 / k
                    except KeyError:
                        pass
                row = df_movies.iloc[i]
                if row["actor_1_name"] in row_reco[["actor_1_name", "actor_2_name", "actor_3_name"]]:
                    score += 1
                if row["actor_2_name"] in row_reco[["actor_1_name", "actor_2_name", "actor_3_name"]]:
                    score += 1
                if row["actor_3_name"] in row_reco[["actor_1_name", "actor_2_name", "actor_3_name"]]:
                    score += 1
                if row["director_name"] == row_reco["director_name"]:
                    score += 1
                if score > max_score:
                    max_score = score

                if total_counter % 10_000 == 0:
                    print("TOTAL_COUNTER :", total_counter)
                total_counter += 1

        # To launch a 10 millisecond beep at each iteration
        frequency = 2500  # Hertz
        duration = 10  # ms
        winsound.Beep(frequency, duration)

        return max_score, total_counter

    # Define the hyperparameters to be tested
    algorithms = ['auto', 'ball_tree', 'kd_tree', 'brute']
    leaf_sizes = [10, 20, 30, 40, 50]  # Testons plusieurs leaf_sizes
    metrics = ['euclidean', 'manhattan']
    p_values = [1, 2]

    # Initializing lists to store results
    best_model_score = 0
    best_params = None

    best_params_details = []

    # Hyperparameter loop
    for algorithm in algorithms:
        for leaf_size in leaf_sizes:
            for metric in metrics:
                for p in p_values:

                    print(f"algorithm: {algorithm},\nleaf_size: {leaf_size},\nmetric: {metric},\np_value: {p}")
                    # KNN model creation with current hyperparameters
                    knn = NearestNeighbors(n_neighbors=51,
                                           algorithm=algorithm,
                                           leaf_size=leaf_size,
                                           metric=metric,
                                           p=p)

                    # Model fitting
                    knn.fit(df_ML.values)
                    score, total_counter = best_score(knn, total_counter)
                    print("SCORE :", score)
                    if score > best_model_score:
                        best_model_score = score
                        best_params = {"algorithm": algorithm,
                                       "leaf_size": leaf_size,
                                       "metric": metric,
                                       "p_value": p}
                        best_params_details.extend([f"score : {score}\n",
                                                    f"params :\n",
                                                    f"algorithm: {algorithm},\nleaf_size: {leaf_size},\n",
                                                    f"metric: {metric},\np_value: {p}\n",
                                                    "-" * 50 + "\n"])

                    # To launch a one-second beep at each iteration in hyperparameters
                    frequency = 2500  # Hertz
                    duration = 1000  # ms
                    winsound.Beep(frequency, duration)

    # We print result and store it in a logging files
    print("best_score :", best_model_score)
    print("best_params :", best_params)
    with open(LOG_DIR / "result.log", "a") as f:
        f.writelines([f"best score : {best_model_score}\n",
                      f"params : {best_params}\n"])
    with open(LOG_DIR / "best_params_detail.log", "a") as f:
        f.writelines(best_params_details)

    # To launch a 10-second beep at the end
    frequency = 2500  # Hertz
    duration = 10_000  # ms
    winsound.Beep(frequency, duration)


if __name__ == "__main__":
    cross_validation()

    # RESULT
    # SCORE: 88.99999999999997
    # best_score: 88.99999999999997
    # best_params: {'algorithm': 'auto', 'leaf_size': 10, 'metric': 'manhattan', 'p_value': 1}
