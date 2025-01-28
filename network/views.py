from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json

from .models import User, Post


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)  # 10 objav na stran
    
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "posts": posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    content = request.POST.get("content")
    if not content:
        return JsonResponse({"error": "Content is required."}, status=400)
    
    post = Post.objects.create(
        user=request.user,
        content=content
    )
    
    return HttpResponseRedirect(reverse("index"))


@login_required
def profile(request, username):
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))
    
    post_list = profile_user.posts.all()
    paginator = Paginator(post_list, 10)
    
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    is_following = request.user.following.filter(id=profile_user.id).exists() if request.user.is_authenticated else False
    
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "followers_count": profile_user.followers_count(),
        "following_count": profile_user.following_count(),
        "is_following": is_following,
        "is_self": request.user == profile_user
    })


@login_required
def follow(request, username):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        user_to_follow = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    
    if request.user == user_to_follow:
        return JsonResponse({"error": "Cannot follow yourself."}, status=400)
    
    if request.user.following.filter(id=user_to_follow.id).exists():
        request.user.following.remove(user_to_follow)
        is_following = False
    else:
        request.user.following.add(user_to_follow)
        is_following = True
    
    return JsonResponse({
        "is_following": is_following,
        "followers_count": user_to_follow.followers_count()
    })


@login_required
def following(request):
    following_users = request.user.following.all()
    post_list = Post.objects.filter(user__in=following_users)
    paginator = Paginator(post_list, 10)
    
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        "posts": posts
    })


@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Objava ne obstaja."}, status=404)
    
    # Preveri, če je trenutni uporabnik lastnik objave
    if post.user != request.user:
        return JsonResponse({"error": "Nimate dovoljenja za urejanje te objave."}, status=403)
    
    # Sprejmi samo PUT zahteve
    if request.method != "PUT":
        return JsonResponse({"error": "PUT zahteva je potrebna."}, status=400)
    
    # Pridobi podatke
    data = json.loads(request.body)
    content = data.get("content", "").strip()
    
    if not content:
        return JsonResponse({"error": "Vsebina ne sme biti prazna."}, status=400)
    
    # Posodobi objavo
    post.content = content
    post.save()
    
    return JsonResponse({
        "message": "Objava uspešno posodobljena.",
        "content": post.content
    })


@login_required
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Objava ne obstaja."}, status=404)
    
    if request.method != "POST":
        return JsonResponse({"error": "POST zahteva je potrebna."}, status=400)
    
    if post.likes.filter(id=request.user.id).exists():
        # Če je uporabnik že všečkal objavo, odstrani všeček
        post.likes.remove(request.user)
        liked = False
    else:
        # Sicer dodaj všeček
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes_count()
    })
