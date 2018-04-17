from decimal import Decimal
from typing import Dict

from django.db.models import QuerySet


def get_min_period_with_delta_price(prices: QuerySet, value: str, price_type: str) -> Dict or None:
    """Функция, которая возвращает минимальный период, когда указанная цена изменилась более чем
    на указанное число

    Args:
        prices (PriceQuerySet): список цен
        value (str): Значение, на которое изменилась цена
        price_type (str): Тип цены

    Returns:
        BeautifulSoup
    """

    prices_values = prices.values('id', 'date', f'delta_{price_type}')
    sum_delta = Decimal('0')
    # складываем последовательно значения дельта
    for price in prices_values:
        sum_delta += abs(price[f'delta_{price_type}'])
        price['sum_delta'] = sum_delta

    result_list = []
    # определяем абсолютное значение дельта для каждого возможного периода
    for j in range(len(prices_values) - 1):
        start_period = prices_values[j]
        for end_period in prices_values[j + 1:]:
            result_list.append(
                {'period': [start_period['date'], end_period['date']],
                 'ids': [start_period['id'], end_period['id']],
                 'absolute_delta': end_period['sum_delta'] - start_period['sum_delta'],
                 'delta_days': abs(start_period['date'] - end_period['date']).days}
            )
    # определяем периоды подходящие под условие и сортируем по величине периода (т.е. разнице в
    # днях между начальной и конечной датами)
    periods = sorted([x for x in result_list if x['absolute_delta'] > Decimal(value)],
                     key=lambda x: x['delta_days'])
    if periods:
        return periods[0]
    return None
