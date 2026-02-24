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
]
