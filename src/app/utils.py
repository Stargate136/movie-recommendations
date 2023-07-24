import pandas as pd
import requests
from bs4 import BeautifulSoup


def load_movies():
    """Function to load movies dataframe

    Returns:
        pd.DataFrame: A dataframe contains all movies
    """
    # We load the dataframe from CSV file
    df = pd.read_csv(
        "https://gist.githubusercontent.com/Stargate136/d861f67493e89a4ad95922a89422c70c/raw/e78c923aa0f3179566b3b00458433a2711fcb812/movie_metadata_cleaned_v2.csv")

    # We fill empty values with an empty string ( Dont worry the dataframe is already cleaned ! )
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
        pd.DataFrame: A dataframe contains movies are recommanded by the Machine Learning algorithm
    """
    # We load the movies dataframe
    df = load_movies()

    # We filter the dataframe by age_category
    df = filter_by_age_category(df, age_category)

    # TODO : modifier la ligne pour utiliser l'algorithme de ML

    data = df.sample(nb * 10)
    return data


def filter_recommendations(df, choices, nb=5):
    """Function to filter recommandations by user choices

    Args:
        df (pd.DataFrame): A dataframe contains movies recommendations
        choices (dict): A dictionnary containing the user choices
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
    """Function to scrapp IMDB website and get the movie image URL

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
