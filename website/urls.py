from django.urls import path,include
from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token
from . import views,views_api

urlpatterns = [
    path('add_bird', views.birds,name='birds'),
    path('create_bird/', views.create_bird, name="create_bird"),
    path('upload_image/', views.upload_image, name="upload_image"),
    path('upload_audio/', views.upload_audio, name="upload_audio"),
    path('delete_bird/', views.delete_bird, name="delete_bird"),
    path('edit_bird/', views.edit_bird, name="edit_bird"),
    path('<int:id>', views.detail_view, name="detail"),
    path('search', views.ajax_search, name="search"),
    path('category', views.category, name="category"),
    path('category/<str:mail>', views.category, name="category"),
    path('likes/', views.likes, name="likes"),
    path('about', views.about,name='about'),
    path('grid', views.grid,name='grid'),
    path('api/', views_api.bird, name="bird"),
    # path('api/token', obtain_auth_token, name="auth_token"),
    path('api/<int:id>', views_api.bird_details, name="bird_details"),
    path('api/category/', views_api.bird_category, name='bird_category'),
]
