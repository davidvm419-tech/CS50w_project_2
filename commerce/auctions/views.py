from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

     # Message to user if is not log in and sent to the log in view
    if request.GET.get("next"):
        messages.error(request, "You must be logged in.")
    
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
        if not title or not description or not initial_bid:
            return render(request, "auctions/newListing.html", {
                "message": "Invalid creation, 1 or more fields were empty."
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
        return render(request, "auctions/newListing.html", {
            "categories": AuctionListing.CATEGORIES,
        })
    

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": AuctionListing.CATEGORIES,
    })


def category_page(request, category):
    selected_category = AuctionListing.objects.filter(category=category)
    return render(request, "auctions/category_page.html", {
        "category": category,
        "listings": selected_category,
    })

def product_details(request, product_id):
    selected_product = AuctionListing.objects.get(pk=product_id)   
    
    return render(request, "auctions/product_details.html", {
        "product": selected_product.title,
        "item": [selected_product],    
    })

@login_required
def bid(request, product_id):
    bid = request.POST["bid"]
    product = AuctionListing.objects.get(pk=product_id)
    
    # Check the input is valid
    try:
        bid = float(bid)
    except (TypeError, ValueError):
        return render(request, "auctions/product_details.html", {
            "message": "Invalid bid value, bid must be a number.",
            "product": product.title,
            "item": [product]
        })
    
    # Check that bid is valid 
    if bid <= product.current_price:
        return render(request, "auctions/product_details.html", {
            "message": "Invalid bid value, bid must be greater than the current price.",
            "product": product.title,
            "item": [product]
        })
    else:
        # Create bid entry
        bid_creation = Bid.objects.create(bidder=request.user, 
                                            product=product, bid_amount=bid)
        
        # Update product price and redirect to product view
        product.current_price = bid
        product.save()
        messages.success(request,"Bid added successfully!")
        return HttpResponseRedirect(reverse("product_details", args=[product_id]))