from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .models import AuctionListing, AuctionComment, Bid, User, WatchList


def index(request):
    auction_list = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        "auction_list": auction_list,
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        last_name = request.POST["last_name"]
        first_name = request.POST["first_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, 
                    first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
@login_required
def newListing(request):
    if request.method == "POST":
        title = request.POST["title"]
        category = request.POST["category"]
        description = request.POST["description"]
        initial_bid = request.POST["initial_bid"]

        # Ensure that fields are not empty
        if not title or not category or not description or not initial_bid:
            return render(request, "auctions/newListing.html", {
                "message": "Invalid creation 1 or more fields were empty."
            })

        # Check if a url is given
        image_url = request.POST["image_url"]
        if image_url == "":
            image_url = None
        
        # Attempt to create listing
        try:
            listing = AuctionListing.objects.create(owner=request.user, category=category, 
                    title=title, description=description, starting_bid=initial_bid, image_url=image_url, current_price=initial_bid)
        except IntegrityError:
            return render(request, "auctions/newListing.html", {
                "message": "Error creating the listing, try again in a few minutes."
            })
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/newListing.html")
