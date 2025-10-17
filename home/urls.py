from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('local-popularity-map', views.local_popularity_map, name='home.local_popularity_map'),

]
