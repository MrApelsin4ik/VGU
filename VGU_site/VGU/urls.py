# urls.py
from django.urls import path
from main_app import views

urlpatterns = [
    path("", views.main_page, name="main_page"),
    path("search/", views.search, name="search"),
    path("news/<int:pk>/", views.news_detail, name="news_detail"),
    path("announcement/<int:pk>/", views.announcement_detail, name="announcement_detail"),
    path("admin/news/create/", views.admin_news_create, name="admin_news_create"),
    path("admin/login/", views.admin_login, name="admin_login"),
]
