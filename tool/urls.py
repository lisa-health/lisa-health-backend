from django.urls import path
from .views import *

urlpatterns = [
    path('aid/', get_aid_tips, name='aid'),
    path('hospital/', get_hospital, name='hospital'),
    path('aid/all/', get_names, name='aid-names')
]
