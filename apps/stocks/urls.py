from django.urls import path

from .views import *

app_name = 'stocks'
urlpatterns = [
    # {% url('stocks:list') %}
    path('', stocks_list_view, name='list'),
    # {% url('stocks:prices') stock.name %}
    path('<str:name>/', stock_prices_list_view, name='prices'),
]
