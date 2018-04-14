from django.urls import path

from .views import *

app_name = 'stocks'
urlpatterns = [
    # {% url('stocks:list') %}
    path('', stocks_list_view, name='list'),
    # {% url('stocks:api_list') %}
    path('api/', stocks_list_api_view, name='api_list'),
    # {% url('stocks:prices') stock.name %}
    path('<str:name>/', stock_prices_list_view, name='prices'),
    # {% url('stocks:api_prices') stock.name %}
    path('api/<str:name>/', stock_prices_list_api_view, name='api_prices'),
]
