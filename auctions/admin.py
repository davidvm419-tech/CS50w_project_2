from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin



from .models import AuctionListing, AuctionComment, Bid, User, WatchList

# Register your models here.
  

class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "category", "title", "description", 
                    "starting_bid", "image_url", "current_price", "created_at", 
                    "is_active", "winner")
    
class AuctionCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "product", "comment", "created_at")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "bidder", "product", "bid_amount", "created_at")

class WatchListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at")

admin.site.register(User, UserAdmin)
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(AuctionComment, AuctionCommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(WatchList, WatchListAdmin)
