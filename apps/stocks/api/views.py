from rest_framework.generics import ListAPIView

from ..models import Stock
from .serializers import StockSerializer

__all__ = (
    'stocks_list_api_view',
)


class StocksListAPIView(ListAPIView):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()

stocks_list_api_view = StocksListAPIView.as_view()
