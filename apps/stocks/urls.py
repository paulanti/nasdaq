from django.urls import path

from .views import *

app_name = 'stocks'
urlpatterns = [
    # {% url('stocks:list') %}
    path('', stocks_list_view, name='list'),
]
