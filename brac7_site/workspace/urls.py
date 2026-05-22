from django.urls import path

from . import views

urlpatterns = [
    path("<int:pk>/", views.design, name="workspace_design"),
    path("<int:pk>/layout/", views.save_layout, name="workspace_save_layout"),
]
