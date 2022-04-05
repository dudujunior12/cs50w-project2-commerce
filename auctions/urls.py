from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("closed", views.closed, name="closed"),
    path("create", views.create, name="create"),
    path("listings/<int:auct_list_id>/bid", views.bid, name="bid"),
    path("listings/<int:auct_list_id>", views.auct_list, name="auct_list"),
    path("listings/<int:auct_list_id>/finish", views.finish, name="finish"),
    path("category", views.category, name="category"),
    path("category/<str:category>", views.categoryResult, name="category-result"),
    path("watchlist", views.watchlist, name="watchlist")
]
