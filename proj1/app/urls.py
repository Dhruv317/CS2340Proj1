
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('restaurants-map/', views.restaurants_map, name='restaurants_map'),
    path('restaurants-map/<float:lat>/<float:lng>/',
         views.restaurants_near_location, name='restaurants_near_location'),
]
