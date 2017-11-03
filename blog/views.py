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
    if request.method == 'POST':
        request_data = json.loads(request.body.decode())
        username = request_data['username']
        password = request_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['POST'])


def signout(request):
    if request.method == 'POST':
        logout(request)
        return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['POST'])


def login_required(function):
    if User.is_authenticated:
        return function
    else:
        return HttpResponse(status=405)


@login_required
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


@login_required
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

        if author_id == 1:
            try:
                article = Article.objects.get(id=article_id)
            except Article.DoesNotExist:
                return HttpResponseNotFound()
            article.title = title
            article.content = content
            article.author_id = author_id
            article.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403) #Unauthorized
    elif request.method == 'DELETE':
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return HttpResponseNotFound()
        # if article.author_id == User.objects.get(username=request.user.get_username()).id:
        if article.author_id == 1:
            article.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403) #Unauthorized
    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])

@login_required
def commentList(request, article_id):
    article_id = int(article_id)
    if request.method == 'GET':
        comments = Article.objects.get(id=article_id).comments.all().values() #type of comments? QuerySet? List?
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


@login_required
def commentDetail(request, comment_id):
    comment_id = int(comment_id)
    if request.method == 'GET':
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponseNotFound()
        return JsonResponse(model_to_dict(comment))
    elif request.method == 'PUT':
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponseNotFound()
        content = json.loads(request.body.decode())['content']
        author_id = json.loads(request.body.decode())['author_id']
        if author_id == 1:
            comment.content = content
            comment.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)
    elif request.method == 'DELETE':
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return HttpResponseNotFound()
        author_id = comment.author_id
        if author_id == 1:
            comment.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])





