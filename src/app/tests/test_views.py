import numpy as np
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from app.utils import generate_recommendations
from app.views import index, questionnaire, result


class IndexViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse('app:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/index.html')

        # Checks that the view returns an HTTP 200 status
        self.assertEqual(response.status_code, 200)

        # Checks that the correct template is used
        self.assertTemplateUsed(response, 'app/index.html')


class QuestionnaireViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_not_allowed_request(self):
        # Test GET request
        request = self.factory.get(reverse('app:questionnaire'))
        response = questionnaire(request)

        # Check the returned status code and message
        self.assertEqual(response.status_code, 405)  # 405 for method not allowed
        self.assertIn("Cette URL n'est pas accessible directement", response.content.decode())

    def test_post_request(self):
        # Test POST request
        response = self.client.post(reverse('app:questionnaire'), data={
            'title': 'Spider-Man 3',
            'recommendationsNumber': '5',
            'age': 'adult',
        })
        # Check the returned status code
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'app/questionnaire.html')

        # Check if the context data is correctly added
        self.assertIn("languages", response.context)
        self.assertIn("genres", response.context)
        self.assertIn("actors", response.context)
        self.assertIn("directors", response.context)
        self.assertIn("title", response.context)
        self.assertIn("nb", response.context)


class ResultViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_not_allowed_request(self):
        # Test GET request
        request = self.factory.get(reverse('app:result'))
        response = result(request)

        # Check the returned status code and message
        self.assertEqual(response.status_code, 405)  # 405 for method not allowed
        self.assertIn("Cette URL n'est pas accessible directement", response.content.decode())

    def test_post_request(self):
        # Test POST request

        # Mocked session data
        title = "Spider-Man 3"
        nb = 5
        recommendations_idx = list(range(51))

        session = self.client.session
        session['title'] = title
        session['nb'] = nb
        session['recommendations_idx'] = recommendations_idx
        session.save()

        response = self.client.post(reverse('app:result'), data={
            "age": "adult",
            "languages": ["English"],
            "duration": ["1"],
            "filter": "genres",
            "genres": ["Action"],
            "actors": [],
            "directors": []
        })

        # Check the returned status code
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'app/result.html')

        # Check if the context data is correctly added
        self.assertIn("title", response.context)
        self.assertIn("nb", response.context)
        self.assertIn("recommended_films", response.context)


class GetMovieTitlesViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request(self):
        # Test GET request
        response = self.client.get(reverse('app:get_movie_titles'))

        # Check the returned status code
        self.assertEqual(response.status_code, 200)

        # Check if the response is a JSON response
        self.assertIsInstance(response.json(), dict)

        # Check if the response data is correctly structured
        data = response.json()
        self.assertIn("adult", data)
        self.assertIn("teenager", data)
        self.assertIn("child", data)
        self.assertIsInstance(data["adult"], list)
        self.assertIsInstance(data["teenager"], list)
        self.assertIsInstance(data["child"], list)
