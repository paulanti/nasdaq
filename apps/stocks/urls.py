from django.urls import path

from .views import *

app_name = 'stocks'
urlpatterns = [
    # {% url('stocks:list') %}
    path('', stocks_list_view, name='list'),
    # {% url('stocks:api_list') %}
    path('api/', stocks_list_api_view, name='api_list'),
    # {% url('stocks:prices') stock.name %}
    path('<slug:name>/', stock_prices_list_view, name='prices'),
    # {% url('stocks:api_prices') stock.name %}
    path('api/<slug:name>/', stock_prices_list_api_view, name='api_prices'),
    # {% url('stocks:prices_analytics') stock.name %}
    path('<slug:name>/analytics/', stock_prices_analytics_view, name='prices_analytics'),
    # {% url('stocks:insiders_list') stock.name %}
    path('<str:name>/insider/', stock_insiders_list_view, name='insiders_list'),
    # {% url('stocks:insider_trades') stock.name, insider.slug %}
    path('<str:name>/insider/<slug:slug>/', insider_trades_list_view, name='insider_trades'),
]
