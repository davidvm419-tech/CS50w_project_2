from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse


from .models import AuctionListing, AuctionComment, Bid, User, WatchList


def index(request):
    auction_list = AuctionListing.objects.filter(is_active=True)
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
        
        # Ensure that fields are not empty
        if not username or not password:
            return render(request, "auctions/register.html", {
                "message": "Username or password fields were empty."
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
                "message": "Invalid creation, 1 or more fields were empty.",
                "categories": AuctionListing.CATEGORIES,
            })

        # Check if a url is given
        image_url = request.POST["image_url"]
        if image_url == "":
            image_url = None
        
        # Attempt to create listing
        try:
            AuctionListing.objects.create(owner=request.user, category=category, 
                    title=title, description=description, starting_bid=initial_bid, image_url=image_url, current_price=initial_bid)
        except IntegrityError:
            return render(request, "auctions/newListing.html", {
                "message": "Error creating the listing, try again in a few minutes.",
                "categories": AuctionListing.CATEGORIES,
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

    # Send the user to an error page in case that the category desn't exist
    categories = [c[0] for c in AuctionListing.CATEGORIES]
    if category not in categories:
        raise Http404("Category does not exist")

    selected_category = AuctionListing.objects.filter(category=category, is_active=True)

    return render(request, "auctions/category_page.html", {
        "category": category,
        "listings": selected_category,
    })


def product_details(request, product_id):  

    # Send user to an error page in case the id doesn't exists 
    selected_product = get_object_or_404(AuctionListing, pk=product_id)

    # Check if user is log in
    if request.user.is_authenticated:
        # Check if product is in user watchlist to render the correct button and to avoid errors if user is not log in
        in_watchlist = WatchList.objects.filter(user=request.user, product=selected_product).exists()
    else:
        in_watchlist = False

    return render(request, "auctions/product_details.html", {
        "product": selected_product.title,
        "item": [selected_product],  
        "in_watchlist": in_watchlist,      
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
    
    # Check that owner can't bid his own product
    if request.user == product.owner:
        messages.error(request, "You cannot bid on your own listing.")
        return HttpResponseRedirect(reverse("product_details", args=[product_id]))
 

    # Create bid entry
    Bid.objects.create(bidder=request.user, product=product, bid_amount=bid)
    
    # Update product price and redirect to product view
    product.current_price = bid
    product.save()
    messages.success(request,"Bid added successfully!")
    return HttpResponseRedirect(reverse("product_details", args=[product_id]))
    
@login_required
def comments(request, product_id):
    comment = request.POST["comment"].strip()
    product = AuctionListing.objects.get(pk=product_id)

    # Check to avoid blank comments
    if not comment:
        return render(request, "auctions/product_details.html", {
            "message": "Comment field empty, please leave a comment.",
            "product": product.title,
            "item": [product]
        })
    
    # Create comment entry
    entry = AuctionComment.objects.create(author=request.user, product=product, comment=comment)
    messages.success(request, "Comment added successfully!")   
    return HttpResponseRedirect(reverse("product_details", args=[product_id])) 

@login_required
def closing_auction(request, product_id):
    product = AuctionListing.objects.get(pk=product_id)

    # Check if user owns the listing
    if request.user != product.owner:
        messages.error(request, "Invaid user, you don't own this listing!")
        return HttpResponseRedirect(reverse("product_details", args=[product_id]))

    # Check if listing is already closed
    if not product.is_active:
        messages.error(request, "Listing already closed!")
        return HttpResponseRedirect(reverse("product_details", args=[product_id]))
    else:
        product.is_active = False    

    # Make the highest bidder the winer and redirect to product page
    highest_bid = product.bids.order_by("-bid_amount").first()
    if highest_bid:
        product.winner = highest_bid.bidder
        product.save()
        messages.success(request, "Auction closed successfully!")    
    else:
        product.save()
        messages.success(request, "Auction closed with no highest bid!")   
    
    return HttpResponseRedirect(reverse("product_details", args=[product_id]))

def watchlist(request):
    # Get user watchlist
    user_watchlist = WatchList.objects.filter(user=request.user)
    # List comprehension to loop over the user watchlist
    products = [item.product for item in user_watchlist]
    return render(request, "auctions/watchlist.html", {
        "products": products,
    })

@login_required
def add_to_watchlist(request, product_id):
    product = AuctionListing.objects.get(pk=product_id)
    # Get the product from the watchlist
    product_in_whatchlist = WatchList.objects.filter(user=request.user, product=product).exists()
    
    # Check if product already in watchlist
    if product_in_whatchlist:
        messages.error(request, "Product already added to your watchlist!")

    else:
        WatchList.objects.create(user=request.user, product=product)
        messages.success(request, "Product added to your watchlist!")
    
    return HttpResponseRedirect(reverse("product_details", args=[product_id]))


@login_required
def delete_from_watchlist(request, product_id):
    product = AuctionListing.objects.get(pk=product_id)
    product_to_delete = WatchList.objects.filter(user=request.user, product=product).exists()

    # Check if product in watchlist
    if product_to_delete:
        WatchList.objects.filter(user=request.user, product=product).delete()
        messages.success(request, "Product successfully deleted from your watchlist!")
    else:
        messages.error(request, "Something went wrong, we can't find the product. Check that product is in your wathlist and try again.")
    
    return HttpResponseRedirect(reverse("product_details", args=[product_id]))
  