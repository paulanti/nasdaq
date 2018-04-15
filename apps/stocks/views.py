from django.db.models import Q
from django.http import Http404
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin

from .mixins import JsonResponseMixin
from .models import Stock, Trade, Insider

__all__ = (
    'stocks_list_view', 'stocks_list_api_view', 'stock_prices_list_view',
    'stock_prices_list_api_view', 'stock_insiders_list_view', 'insider_trades_list_view',
    'stock_prices_analytics_view', 'stock_prices_analytics_api_view'
)


class StocksListView(ListView):
    model = Stock
    context_object_name = 'stocks'
    template_name = 'stocks/stocks_list.html'

stocks_list_view = StocksListView.as_view()


class StocksListAPIView(JsonResponseMixin, StocksListView):
    pass

stocks_list_api_view = StocksListAPIView.as_view()


class StockPricesListView(SingleObjectMixin, ListView):
    template_name = 'stocks/stock_prices.html'
    queryset = Stock.objects.all()
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.queryset)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.object.prices.all()

stock_prices_list_view = StockPricesListView.as_view()


class StockPricesAnalyticsView(StockPricesListView):
    template_name = 'stocks/stock_prices_analytics.html'

    def get_object(self, queryset=None):
        if 'date_from' not in self.request.GET or 'date_to' not in self.request.GET:
            raise Http404('Dates aren\'t specified')
        return super().get_object(queryset)

    def get_queryset(self):
        qs = super().get_queryset()
        get_params = self.request.GET
        date_from = get_params.get('date_from')
        date_to = get_params.get('date_to')
        return qs.filter(Q(date__date=date_from) | Q(date__date=date_to))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_price = self.object_list.first()
        first_price = self.object_list.last()
        for price in ('open', 'high', 'low', 'close', 'volume'):
            context[f'delta_{price}'] = getattr(last_price, price) - getattr(first_price, price)
        return context

stock_prices_analytics_view = StockPricesAnalyticsView.as_view()


class StockPricesListAPIView(JsonResponseMixin, StockPricesListView):
    pass

stock_prices_list_api_view = StockPricesListAPIView.as_view()


class StockInsidersListView(SingleObjectMixin, ListView):
    template_name = 'stocks/stock_insiders.html'
    queryset = Stock.objects.all()
    slug_field = 'name'
    slug_url_kwarg = 'name'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.queryset)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Trade.objects.filter(insider_relation__stock=self.object).reverse()

stock_insiders_list_view = StockInsidersListView.as_view()


class InsiderTradesListView(SingleObjectMixin, ListView):
    template_name = 'stocks/insider_trades.html'
    queryset = Insider.objects.all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.queryset)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Trade.objects.filter(insider_relation__insider=self.object).reverse()

insider_trades_list_view = InsiderTradesListView.as_view()
