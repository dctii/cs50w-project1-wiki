from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    # <str:title> <-- will take in a string that passes data 'title' into the path to dynamically go to the correct entry page
    path('wiki/<str:title>', views.entry, name="entry"),
    path('entry_handler', views.entry_handler, name="entry_handler"),
    # <str:title> <-- will take in a string that passes data 'title' into the path to dynamically go to the correct entry edit page
    path('wiki/<str:title>/edit', views.edit, name="edit"),
    path('random', views.random, name="random"),
    path('search', views.search, name="search")
    ]