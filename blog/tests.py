from django.test import TestCase, Client
from django.http import HttpResponseNotAllowed
from .models import User, Article, Comment
from .views import login_required
import json


class BlogTestCase(TestCase):

    def setUp(self):
        u1 = User.objects.create_user(username='User1', password='user1pwd',)
        self.credentials = u1
        User.objects.get(id=1).is_active = True

        User.objects.create_user(username='User2', password='user2pwd')
        User.objects.create_user(username='User3', password='user3pwd')

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

    def test_article_list_get_not_found(self):
        response = self.client.get('/api/article/5')
        self.assertEqual(response.status_code, 404)

    def test_article_detail_get(self):
        response = self.client.get('/api/article/1')
        loaded_data = json.loads(response.content.decode())
        data = {'author': 1, 'content': 'article1 content', 'id': 1, 'title': 'article1'}
        self.assertEqual(loaded_data, data)
        self.assertEqual(response.status_code, 200)

    def test_article_detail_put_authorized(self):
        response = self.client.put('/api/article/1',
                                   json.dumps(
                                       {'author_id': 1, 'content': 'article1 modified content',
                                        'id': 1, 'title': 'article1 modified'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_article_detail_put_unauthorized(self):
        response = self.client.put('/api/article/3',
                                   json.dumps(
                                       {'author_id': 2, 'content': 'article3 modifed content',
                                        'id': 3, 'title': 'article3 modified'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_article_detail_put_not_found(self):
        response = self.client.put('/api/article/5',
                                   json.dumps(
                                       {'author_id': 1, 'content': 'article5 fake',
                                        'id': 5, 'title': 'article5 put'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_article_detail_post(self):
        response = self.client.post('/api/article/1',
                                    json.dumps(
                                       {'author_id': 1, 'content': 'fake article1',
                                        'id': 1, 'title': 'article1 post'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_article_detail_delete_authorized(self):
        response = self.client.delete('/api/article/1')
        self.assertEqual(response.status_code, 200)

    def test_article_detail_delete_unauthorized(self):
        response = self.client.delete('/api/article/3')
        self.assertEqual(response.status_code, 403)

    def test_article_detail_delete_not_found(self):
        response = self.client.delete('/api/article/5')
        self.assertEqual(response.status_code, 404)

    def test_comment_list_get(self):
        response = self.client.get('/api/article/1/comment')
        loaded_data = json.loads(response.content.decode())
        data = [{'id': 1, 'content': 'comment1', 'author_id': 2, 'article_id': 1},
                {'id': 2, 'content': 'comment2', 'author_id': 1, 'article_id': 1}]
        self.assertEqual(loaded_data, data)
        self.assertEqual(response.status_code, 200)

    def test_comment_list_post(self):
        response = self.client.post('/api/article/1/comment',
                                    json.dumps({'content': 'comment4', 'author_id': 1, 'article_id': 1}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_comment_list_put(self):
        response = self.client.put('/api/article/1/comment',
                                   json.dumps({'content': 'comment5', 'author_id':1, 'article_id': 1}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_comment_list_delete(self):
        response = self.client.delete('/api/article/1/comment')
        self.assertEqual(response.status_code, 405)

    def test_comment_detail_get(self):
        response = self.client.get('/api/comment/1')
        loaded_data = json.loads(response.content.decode())
        data = {'id': 1, 'content': 'comment1', 'author': 2, 'article': 1}
        self.assertEqual(loaded_data, data)
        self.assertEqual(response.status_code, 200)

    def test_comment_detail_get_not_found(self):
        response = self.client.get('/api/comment/5')
        self.assertEqual(response.status_code, 404)

    def test_comment_detail_put_unauthorized(self):
        response = self.client.put('/api/comment/1',
                                   json.dumps({'content': 'comment1 modified', 'author_id': 2, 'article_id': 1}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_comment_detail_put_authorized(self):
        response = self.client.put('/api/comment/2',
                                   json.dumps({'content': 'comment2 modified', 'author_id': 1, 'article_id': 1}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_comment_detail_put_not_found(self):
        response = self.client.put('/api/comment/5',
                                   json.dumps({'content': 'comment5 modified', 'author_id': 1, 'article_id': 1}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_comment_detail_delete_unauthorized(self):
        response = self.client.delete('/api/comment/1')
        self.assertEqual(response.status_code, 403)

    def test_comment_detail_delete_authorized(self):
        response = self.client.delete('/api/comment/2')
        self.assertEqual(response.status_code, 200)

    def test_comment_detail_delete_not_found(self):
        response = self.client.delete('/api/comment/5')
        self.assertEqual(response.status_code, 404)

    def test_comment_detail_post(self):
        response = self.client.post('/api/comment/4',
                                    json.dumps({'content': 'comment4', 'author_id':1, 'article_id': 1}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_signin_post_valid_user(self):
        username = 'User1'
        password = 'user1pwd'
        response = self.client.post('/api/signin',
                                    json.dumps({'username': username, 'password': password}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_signin_post_invalid_user(self):
        username = 'User4'
        password = 'user4pwd'
        response = self.client.post('/api/signin',
                                    json.dumps({'username': username, 'password': password}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_signin_get_not_allowed(self):
        response = self.client.get('/api/signin')
        self.assertEqual(response.status_code, 405)

    def test_signin_put_not_allowed(self):
        username = 'User1'
        password = 'user1pwd'
        response = self.client.put('/api/signin',
                                   json.dumps({'username': username, 'password': password}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_signin_delete_not_allowed(self):
        response = self.client.delete('/api/signin')
        self.assertEqual(response.status_code, 405)

    def test_signout_post(self):
        response = self.client.post('/api/signout',
                                    json.dumps({'username': 'User1', 'password':'user1pwd'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_signout_get_not_allowed(self):
        response = self.client.get('/api/signout')
        self.assertEqual(response.status_code, 405)

    def test_signout_put_not_allowed(self):
        response = self.client.put('/api/signout',
                                   json.dumps({'username': 'User1', 'password':'user1pwd'}),
                                              content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_login_required_logined(self):
        def is_logined():
            return True
        self.assertEqual(login_required(is_logined()), True)

    def test_login_required_not_logined(self):
        def is_logined():
            return True
        User.is_authenticated = False
        self.assertEqual(login_required(is_logined()).status_code, 405)







