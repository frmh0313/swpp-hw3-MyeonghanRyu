from django.test import TestCase, Client
from django.http import HttpResponseNotAllowed
from .models import User, Article, Comment
import json


class BlogTestCase(TestCase):

    def setUp(self):
        User.objects.create(username='User1', password='user1pwd')
        User.objects.create(username='User2', password='user2pwd')
        User.objects.create(username='User3', password='user3pwd')

        Article.objects.create(title='article1', content='article1 content', author=User.objects.get(id=1))
        Article.objects.create(title='article2', content='article2 content', author=User.objects.get(id=1))
        Comment.objects.create(content='comment1', author=User.objects.get(id=2), article=Article.objects.get(id=1))
        Comment.objects.create(content='comment2', author=User.objects.get(id=1), article=Article.objects.get(id=1))
        Comment.objects.create(content='comment3', author=User.objects.get(id=3), article=Article.objects.get(id=2))

        Article.objects.create(title='article3', content='article3 content', author=User.objects.get(id=2))

        self.client = Client()

    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup', json.dumps({'username': 'chris', 'password': 'chris'}), content_type='application/json')
        self.assertEqual(response.status_code, 403) # Request without csrf token returns 403 response

        response = client.get('/api/token')
        csrftoken = response.cookies['csrftoken'].value # Get csrf token from cookie

        response = client.post('/api/signup', json.dumps({'username': 'chris', 'password': 'chris'}), content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201) # Pass csrf protection

    def test_csrf_post(self):
        response = self.client.post('/api/token', data={})
        self.assertEqual(response.status_code, 405)

    def test_csrf_put(self):
        response = self.client.put('/api/token', data=[])
        self.assertEqual(response.status_code, 405)

    def test_csrf_delete(self):
        response = self.client.delete('/api/token')
        self.assertEqual(response.status_code, 405)

    def test_signup_get(self):
        response = self.client.get('/api/signup')
        self.assertEqual(response.status_code, 405)

    def test_signup_put(self):
        response = self.client.put('/api/signup', data=[])
        self.assertEqual(response.status_code, 405)

    def test_signup_delete(self):
        response = self.client.put('/api/signup')
        self.assertEqual(response.status_code, 405)

    def test_article_list_get(self):
        response = self.client.get('/api/article')
        loaded_data = json.loads(response.content.decode())
        data = [{'author_id': 1, 'content': 'article1 content', 'id': 1, 'title': 'article1'},
                {'author_id': 1, 'content': 'article2 content', 'id': 2, 'title': 'article2'},
                {'author_id': 2, 'content': 'article3 content', 'id': 3, 'title': 'article3'}]
        self.assertEqual(loaded_data, data)
        self.assertEqual(response.status_code, 200)

    def test_article_list_post(self):
        response = self.client.post('/api/article',
                                    json.dumps({'author_id': 2, 'content': 'testing article', 'title': 'testing'}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_article_list_put(self):
        response = self.client.put('/api/article', data=[])
        self.assertEqual(response.status_code, 405)

    def test_article_list_delete(self):
        response = self.client.delete('/api/article', data=[])
        self.assertEqual(response.status_code, 405)

    def test_article_detail_get(self):
        response = self.client.get('/api/article/1')
        loaded_data = json.loads(response.content.decode())
        data = {'author_id': 1, 'content': 'article1 content', 'id': 1, 'title': 'article1'}
        self.assertEqual(loaded_data, data)
        self.assertEqual(response.status_code, 200)

    def test_article_detail_put(self):
        response = self.client.put('/api/article/1',
                                   json.dumps({'author_id':1, 'content': 'article1 modified content', 'id': 1, 'title': 'article1 modified'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_article_detail_post(self):
        response = self.client.put('/api/article/1', data=[])
        self.assertEqual(response.status_code, 405)

    def test_article_detail_delete(self):
        response = self.client.delete('/api/article/1')
        self.assertEqual(response.status_code, 200)




