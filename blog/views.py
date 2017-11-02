from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import JsonResponse, HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.forms.models import model_to_dict
from .models import Article, User, Comment
import json


def signup(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        User.objects.create_user(username=username, password=password)
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['POST'])


@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])


def signin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=401)


def signout(request):
    logout(request)


def articleList(request):
    if request.method == 'GET':
        return JsonResponse(list(Article.objects.all().values()), safe=False)
    elif request.method == 'POST':
        title = json.loads(request.body.decode())['title']
        content = json.loads(request.body.decode())['content']
        author_id = json.loads(request.body.decode())['author_id']
        new_article = Article(title=title, content=content, author_id=author_id)
        new_article.save()
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


def articleDetail(request, article_id):
    article_id = int(article_id)
    if request.method == 'GET':
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponseNotFound()
        return JsonResponse(model_to_dict(article))
    elif request.method == 'PUT':
        title = json.loads(request.body.decode())['title']
        content = json.loads(request.body.decode())['content']
        author_id = json.loads(request.body.decode())['author_id']
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponseNotFound()
        article.title = title
        article.content = content
        article.author_id = author_id
        article.save()
        return HttpResponse(status=204)
    elif request.method == 'DELETE':
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponseNotFound()
        article.delete()
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


def commentList(request, article_id):
    article_id = int(article_id)
    if request.method == 'GET':
        try:
            comments = Article.objects.get(id=article_id).comments.all().values() #type of comments? QuerySet? List?
            print(type(comments))
        except Comment.DoesNotExist:
            return HttpResponseNotFound()
        return JsonResponse(list(comments), safe=False)
    elif request.method == 'POST':
        content = json.loads(request.body.decode())['content']
        author_id = json.loads(request.body.decode())['author_id']
        new_comment = Comment(article_id=article_id, content=content, author_id=author_id,
                              article=Article.objects.get(id=article_id))
        new_comment.save()
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


def commentDetail(request, comment_id):
    comment_id = int(comment_id)
    if request.method == 'GET':
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponseNotFound()
        return JsonResponse(model_to_dict(comment))
    elif request.method == 'PUT':
        # article_id = json.loads(request.body.decode())['article_id']
        content = json.loads(request.body.decode())['content']
        author_id = json.loads(request.body.decode())['author_id']
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponseNotFound()
        # comment.article_id = article_id # article modifying not allowed
        comment.content = content
        # comment.author_id = author_id # author_id modifying not allowed
        comment.save()
        return HttpResponse(status=204)
    elif request.method == 'DELETE':
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponseNotFound()
        comment.delete()
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])







