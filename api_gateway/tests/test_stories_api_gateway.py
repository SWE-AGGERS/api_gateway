import unittest
from unittest import mock
from api_gateway.app import create_app


class TestApp(unittest.TestCase):

    def test1(self):
        _app = create_app()
        with _app.test_client() as client:
            with mock.patch('api_gateway.views.stories.get_users_s') as get_user_mock:
                with mock.patch('api_gateway.views.stories.get_stories_s') as get_stories_mock:
                    with mock.patch('api_gateway.views.stories.is_follower_s') as is_follower_mock:
                        get_user_mock.return_value = {
                                "firstname": "luca",
                                "lastname": "perez",
                                "email": "example@example.com",
                                "dateofbirth": "19/01/01",
                                "user_id": 1
                        }

                        get_stories_mock.return_value = [
                            {
                                'id': 1,
                                'text': 'diodiddio',
                                'dicenumber': 0,
                                'roll': {},
                                'date': '1/1/1',
                                'likes': 0,
                                'dislikes': 1,
                                'author_id': 1}
                            ]

                        is_follower_mock.return_value = True

                        reply = client.get('/stories')
                        self.assertEqual(reply.status_code, 200)

    def test2(self):
        app = create_app().test_client()
        reply = app.get('/stories/nonExistingID')
        self.assertEqual(reply.status_code, 404)
