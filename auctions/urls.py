from django.urls import path

from . import views

urlpatterns = [
    # Index url
    path("", views.index, name="index"),

    # User urls
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # Categories urls
    path("newListing", views.newListing, name="newListing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category_page, name="category_page"),
    
    # Listing urls
    path("listing/<int:product_id>", views.product_details, name="product_details"),
    path("listing/<int:product_id>/bid", views.bid, name="bid"),
    path("listing/<int:product_id>/comments", views.comments, name="comments"),
    path("listing/<int:product_id>/closing_auction", views.closing_auction, name="closing_auction"),
    path("listing/<int:product_id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("listing/<int:product_id>/delete_from_watchlist", views.delete_from_watchlist, name="delete_from_watchlist"),
    
    # Watchlist urls
    path("watchlist", views.watchlist, name="watchlist"),
]
