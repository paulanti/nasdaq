from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin

from .mixins import JsonResponseMixin
from .models import Stock

__all__ = ['stocks_list_view', 'stocks_list_api_view', 'stock_prices_list_view',
           'stock_prices_list_api_view']


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


class StockPricesListAPIView(JsonResponseMixin, StockPricesListView):
    pass

stock_prices_list_api_view = StockPricesListAPIView.as_view()
