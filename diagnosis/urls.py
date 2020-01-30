from django.urls import path
from diagnosis.views import *

urlpatterns = [
    path('predict/', predict, name='predict'),
    path('relate/', relate, name='relate')
]
