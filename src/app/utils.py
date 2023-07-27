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
    return df.iloc[idx, :]


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


def generate_recommendations(title="", nb=5, age_category="adult"):
    """Function to generate recommendations using Machine Learning

    Args:
        title (str, optional): The title of the movie the user choosed. Defaults to "".
        nb (int, optional): Number of recommandations the user want. Defaults to 5.
        age_category (str, optional): A string representing the category of age. Possibles values : ["child", "teenager", "adult"]. Defaults to "adult".

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
    nn = NearestNeighbors(n_neighbors=nb * 10)
    nn.fit(df_ML.drop("idx", axis=1))

    # We get the index of the movie with his title, and we get the neighbors
    idx = df_movies[df_movies["movie_title"] == title].index
    distances, indices = nn.kneighbors(df_ML.iloc[idx].drop("idx", axis=1))

    # We get the indexes of the movies (except the first, it's the input movie)
    indices = df_ML.iloc[indices[0, 1:]]["idx"].values

    # And we load the recommendations in a dataframe
    df_recommendations = load_recommendations(indices)

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
    times = choices["times"]
    if times:
        temp_df = None
        for time in times:
            if time == "0":
                mask = df["duration"] < 90
                temp_df = pd.concat([temp_df, df[mask]])
            if time == "1":
                mask_1 = df["duration"] >= 90
                mask_2 = df["duration"] < 120
                temp_df = pd.concat([temp_df, df[mask_1 & mask_2]])
            if time == "2":
                mask_1 = df["duration"] >= 120
                mask_2 = df["duration"] < 180
                temp_df = pd.concat([temp_df, df[mask_1 & mask_2]])
            if time == "3":
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


if __name__ == "__main__":
    title = "Spider-Man 3"
    nb_recommendations = 10
    age_category = "adult"
    user_choices = {"languages": None,
                    "times": None,
                    "filter": None}

    df_recommendations = generate_recommendations(title=title, nb=nb_recommendations, age_category=age_category)
    df_recommendations = filter_recommendations(df=df_recommendations, choices=user_choices, nb=nb_recommendations)
    print(df_recommendations)