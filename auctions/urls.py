from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("my_listings", views.my_listing, name="my_listings"),
    path("my_bids", views.my_bids, name="my_bids"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.filter, name="filter"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("update/<int:listing_id>", views.update, name="update"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("close/<int:listing_id>", views.close, name="close")
]
