import imghdr
import requests
import unittest

import pandas as pd

from app.utils import load_movies, load_recommendations, filter_by_age_category, generate_recommendations, \
    filter_recommendations, get_thumbnail_url


class LoadMoviesTest(unittest.TestCase):
    def test_load_movies(self):
        # Call the function
        df = load_movies()

        # Check that the result is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Check that the DataFrame has the expected columns
        # Replace with the actual column names of your DataFrame
        expected_columns = ["movie_title", "director_name", "num_critic_for_reviews", "duration",
                            "director_facebook_likes", "actor_3_facebook_likes", "actor_2_name",
                            "actor_1_facebook_likes", "gross", "genres", "actor_1_name",
                            "num_voted_users", "cast_total_facebook_likes", "actor_3_name",
                            "plot_keywords", "movie_imdb_link", "num_user_for_reviews", "language",
                            "country", "content_rating", "budget", "title_year", "actor_2_facebook_likes",
                            "imdb_score", "movie_facebook_likes", "gross_filled_with_median",
                            "budget_filled_with_median", "age_category"]  # A list of column names
        for column in expected_columns:
            self.assertIn(column, df.columns)


class LoadRecommendationsTest(unittest.TestCase):
    def test_load_recommendations(self):
        # Call the function with some indices
        indices = [0, 1, 2]  # Use some indices that you know should work
        df = load_recommendations(indices)

        # Check that the result is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Check that the DataFrame has the expected number of rows
        self.assertEqual(len(df), len(indices))

        # Check that the DataFrame only contains rows with the expected indices
        self.assertListEqual(df.index.tolist(), indices)


class FilterByAgeCategoryTest(unittest.TestCase):
    def setUp(self):
        # Create a test DataFrame
        self.df = pd.DataFrame({
            "age_category": ["adult", "teenager", "child", "unknown"],
            "other_column": ["a", "b", "c", "d"]
        })

    def test_filter_by_age_category(self):
        # Test filtering for "adult"
        filtered_df = filter_by_age_category(self.df, "adult")
        self.assertEqual(len(filtered_df), 4)  # All rows should be included
        self.assertEqual(set(filtered_df["age_category"]), {"adult", "teenager", "child", "unknown"})

        # Test filtering for "teenager"
        filtered_df = filter_by_age_category(self.df, "teenager")
        self.assertEqual(len(filtered_df), 3)  # Only "adult" should be excluded
        self.assertEqual(set(filtered_df["age_category"]), {"teenager", "child", "unknown"})

        # Test filtering for "child"
        filtered_df = filter_by_age_category(self.df, "child")
        self.assertEqual(len(filtered_df), 2)  # Only "child" and "unknown" should be included
        self.assertEqual(set(filtered_df["age_category"]), {"child", "unknown"})


class GenerateRecommendationsTest(unittest.TestCase):
    def test_generate_recommendations(self):
        # Choose a known movie from your test data
        title = "Spider-Man 3"
        nb = 5
        age_category = "adult"

        # Call the function
        df = generate_recommendations(title=title, nb=nb, age_category=age_category)

        # Check that the result is a DataFrame
        self.assertIsInstance(df, pd.DataFrame)

        # Check that the DataFrame has the expected number of rows
        self.assertEqual(len(df), 50)

        # Check that the DataFrame does not contain the input movie
        self.assertNotIn(title, df["movie_title"])


class FilterRecommendationsTest(unittest.TestCase):
    def setUp(self):
        # Create a test DataFrame
        self.df = pd.DataFrame({
            "language": ["English", "French", "Spanish", "German"],
            "duration": [90, 120, 150, 180],
            "genres": ["Drama|Comedy", "Action|Adventure", "Horror|Thriller", "Sci-Fi|Fantasy"],
            "actor_1_name": ["Actor 1", "Actor 2", "Actor 3", "Actor 4"],
            "director_name": ["Director 1", "Director 2", "Director 3", "Director 4"]
        })

    def test_filter_recommendations(self):
        # Test filtering by language
        choices = {"languages": ["English", "French"],
                   "duration": [],
                   "filter": "",
                   "genres": [],
                   "actors": [],
                   "directors": []}
        filtered_df = filter_recommendations(self.df, choices)
        self.assertEqual(set(filtered_df["language"]), set(choices["languages"]))

        # Test filtering by duration
        choices = {"languages": [],
                   "duration": ["1", "2"],
                   "filter": "",
                   "genres": [],
                   "actors": [],
                   "directors": []}
        filtered_df = filter_recommendations(self.df, choices)
        self.assertTrue(all(90 <= duration < 180 for duration in filtered_df["duration"]))

        # Test filtering by genres
        choices = {"languages": [],
                   "duration": [],
                   "filter": "genres",
                   "genres": ["Drama", "Comedy"],
                   "actors": [],
                   "directors": []}
        filtered_df = filter_recommendations(self.df, choices, nb=1)
        self.assertEqual(filtered_df.iloc[0]["genres"], "Drama|Comedy")

        # Test filtering by actor
        choices = {"languages": [],
                   "duration": [],
                   "filter": "actors",
                   "genres": [],
                   "actors": ["Actor 1"],
                   "directors": []}
        filtered_df = filter_recommendations(self.df, choices, nb=1)
        self.assertEqual(filtered_df.iloc[0]["actor_1_name"], "Actor 1")

        # Test filtering by director
        choices = {"languages": [],
                   "duration": [],
                   "filter": "directors",
                   "genres": [],
                   "actors": [],
                   "directors": ["Director 1"]}
        filtered_df = filter_recommendations(self.df, choices, nb=1)
        self.assertEqual(filtered_df.iloc[0]["director_name"], "Director 1")


class GetThumbnailUrlTest(unittest.TestCase):
    def test_get_thumbnail_url(self):
        # Test with a known movie URL
        url = "http://www.imdb.com/title/tt0472259/?ref_=fn_tt_tt_1"
        thumbnail_url = get_thumbnail_url(url)

        # Check that the returned URL is a string
        self.assertIsInstance(thumbnail_url, str)

        # Check that the URL is an image by downloading the image and checking its type
        response = requests.get(thumbnail_url)
        image_type = imghdr.what(None, response.content)
        self.assertIn(image_type, ["jpeg", "png", "gif"])
