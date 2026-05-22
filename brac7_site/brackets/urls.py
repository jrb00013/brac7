from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("new/", views.create_bracket, name="create_bracket"),
    path("<int:pk>/", views.bracket_detail, name="bracket_detail"),
    path("<int:pk>/design/", views.bracket_workspace_link, name="bracket_design"),
    path("<int:pk>/export/<str:fmt>/", views.export_file, name="export_file"),
    path("<int:pk>/api/winner/", views.api_set_winner, name="api_set_winner"),
]
