from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('local-popularity-map', views.local_popularity_map, name='home.local_popularity_map'),

    # ✅ API endpoint used by the map JS
    path('api/top_movies_by_state/', views.top_movies_by_state, name='home.top_movies_by_state'),
]
