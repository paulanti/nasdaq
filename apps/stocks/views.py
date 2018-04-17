from django.http import Http404
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin

from .models import Stock, Trade, Insider

__all__ = (
    'stocks_list_view', 'stock_prices_list_view', 'stock_insiders_list_view',
    'insider_trades_list_view', 'stock_prices_analytics_view', 'stock_prices_delta_view'
)


class StocksListView(ListView):
    model = Stock
    context_object_name = 'stocks'
    template_name = 'stocks/stocks_list.html'

stocks_list_view = StocksListView.as_view()


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


class StockPricesAnalyticsView(StockPricesListView):
    template_name = 'stocks/stock_prices_analytics.html'

    def get_object(self, queryset=None):
        if 'date_from' not in self.request.GET or 'date_to' not in self.request.GET:
            raise Http404('Dates aren\'t specified')
        return super().get_object(queryset)

    def get_queryset(self):
        qs = super().get_queryset().reverse()
        return qs.get_delta_between_dates(self.request)

stock_prices_analytics_view = StockPricesAnalyticsView.as_view()


class StockPricesDeltaView(StockPricesListView):
    template_name = 'stocks/stock_prices_delta.html'

    def get_object(self, queryset=None):
        if 'value' not in self.request.GET or 'type' not in self.request.GET:
            raise Http404('Value and type aren\'t specified')
        return super().get_object(queryset)

    def get_queryset(self):
        qs = super().get_queryset().reverse()
        return qs.get_prices_for_delta(self.request)

stock_prices_delta_view = StockPricesDeltaView.as_view()
