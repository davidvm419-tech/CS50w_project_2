from django.contrib.auth.models import AbstractUser
from django.db import models

# Fill the default class parameters, not custom values for now
class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    # Default categories
    CATEGORIES = [
        ("WEAPONS", "Weapons"),
        ("ARMOR", "Armor"),
        ("MOUNTS", "Mounts"),
        ("CONTAINERS", "Containers"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings"    )
    category = models.CharField(max_length=25, choices=CATEGORIES, default="WEAPONS")
    title = models.CharField(max_length= 64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="wins")

    # Order listings by newest creation date
    class Meta:
        ordering = ["-created_at"]


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    product = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class AuctionComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    product = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Order comments by newest creation date
    class Meta:
        ordering = ["-created_at"]
    

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    product = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watchlist_by")

    # Constrain user to only add the same product once to the watchlist avoiding not necessary duplicates
    class Meta:
        # This is the correct name variable
        unique_together = ("user", "product")
        