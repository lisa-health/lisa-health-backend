from django.urls import path
from wiki.views import *

urlpatterns = [
    path('disease/', disease_info, name='disease'),
    path('search/', search_disease, name='search')
]
