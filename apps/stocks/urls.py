from django.urls import path, include

from .views import *
from .api.views import *

app_name = 'stocks'
urlpatterns = [
    # {% url('stocks:list') %}
    path('', stocks_list_view, name='list'),
    # {% url('stocks:api_list') %}
    path('api/', stocks_list_api_view, name='api_list'),
    path('<slug:name>/', include([
        # {% url('stocks:prices') stock.name %}
        path('', stock_prices_list_view, name='prices'),
        # {% url('stocks:prices_analytics') stock.name %}
        path('analytics/', stock_prices_analytics_view, name='prices_analytics'),
        path('insider/', include([
            # {% url('stocks:insiders_list') stock.name %}
            path('', stock_insiders_list_view, name='insiders_list'),
            # {% url('stocks:insider_trades') stock.name, insider.slug %}
            path('<slug:slug>/', insider_trades_list_view, name='insider_trades')
        ]))
    ])),
    path('api/<slug:name>/', include([
        # {% url('stocks:api_prices') stock.name %}
        path('', stock_prices_list_api_view, name='api_prices'),
        # {% url('stocks:api_prices_analytics') stock.name %}
        path('analytics/', stock_prices_analytics_api_view, name='api_prices_analytics'),
        path('insider/', include([
            # {% url('stocks:api_insiders_list') stock.name %}
            path('', stock_insiders_list_api_view, name='api_insiders_list'),
            # {% url('stocks:api_insider_trades') stock.name, insider.slug %}
            path('<slug:slug>/', insider_trades_list_api_view, name='api_insider_trades')
        ]))
    ])),
]
