from rest_framework.generics import ListAPIView

from ..models import Stock, Price, Trade
from .serializers import StockSerializer, PriceSerializer, TradeSerializer, InsiderTradesSerializer, \
    PriceAnalyticsSerializer

__all__ = (
    'stocks_list_api_view', 'stock_prices_list_api_view', 'stock_insiders_list_api_view',
    'insider_trades_list_api_view', 'stock_prices_analytics_api_view'
)


class StocksListAPIView(ListAPIView):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()

stocks_list_api_view = StocksListAPIView.as_view()


class StockPricesListAPIView(ListAPIView):
    serializer_class = PriceSerializer
    queryset = Price.objects.all()
    lookup_field = 'stock__name'
    lookup_url_kwarg = 'name'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{self.lookup_field: self.kwargs[self.lookup_url_kwarg]})

stock_prices_list_api_view = StockPricesListAPIView.as_view()


class StockInsidersListAPIView(ListAPIView):
    serializer_class = TradeSerializer
    queryset = Trade.objects.all().reverse()
    lookup_field = 'insider_relation__stock__name'
    lookup_url_kwarg = 'name'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{self.lookup_field: self.kwargs[self.lookup_url_kwarg]})

stock_insiders_list_api_view = StockInsidersListAPIView.as_view()


class InsiderTradesListAPIView(StockInsidersListAPIView):
    serializer_class = InsiderTradesSerializer
    lookup_field = 'insider_relation__insider__slug'
    lookup_url_kwarg = 'slug'

insider_trades_list_api_view = InsiderTradesListAPIView.as_view()


class StockPricesAnalyticsAPIView(StockPricesListAPIView):
    serializer_class = PriceAnalyticsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.get_delta_between_dates(self.request)

stock_prices_analytics_api_view = StockPricesAnalyticsAPIView.as_view()
