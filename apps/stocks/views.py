from django.views.generic import ListView

from .models import Stock

__all__ = ['stocks_list_view']


class StocksListView(ListView):
    model = Stock
    context_object_name = 'stocks'
    template_name = 'stocks/stocks_list.html'

stocks_list_view = StocksListView.as_view()
