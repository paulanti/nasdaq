from django.db import models
from django.db.models import Window, F, Q
from django.db.models.functions import Lag


class PriceQuerySet(models.QuerySet):

    def with_delta(self):
        qs = self.annotate(
            prev_open=Window(
                expression=Lag('open', default=F('open')),
                order_by=F('date').asc(),
            ),
            prev_high=Window(
                expression=Lag('high', default=F('high')),
                order_by=F('date').asc(),
            ),
            prev_low=Window(
                expression=Lag('low', default=F('low')),
                order_by=F('date').asc(),
            ),
            prev_close=Window(
                expression=Lag('close', default=F('close')),
                order_by=F('date').asc(),
            ),
            prev_volume=Window(
                expression=Lag('volume', default=F('volume')),
                order_by=F('date').asc(),
            )
        )
        qs = qs.annotate(
            delta_open=F('open') - F('prev_open'),
            delta_high=F('high') - F('prev_high'),
            delta_low=F('low') - F('prev_low'),
            delta_close=F('close') - F('prev_close'),
            delta_volume=F('volume') - F('prev_volume')
        )
        return qs

    def get_delta_between_dates(self, request):
        """Функция для получения разницы цен в датах
        """
        get_params = request.GET
        date_from = get_params.get('date_from')
        date_to = get_params.get('date_to')
        return self.with_delta().filter(Q(date__date=date_from) | Q(date__date=date_to))
