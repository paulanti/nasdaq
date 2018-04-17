from typing import List, Tuple

import itertools
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils import timezone

from apps.stocks.models import Stock, Insider, Relation, Trade, Price


def get_stocks_list(path: str) -> List:
    with open(path) as file:
        stock_list = file.read().splitlines()
    return stock_list


class NasdaqParser:
    """Класс для парсинга Nasdaq.com

    Attributes:
        stocks (list): Список акций для парсинга
    """

    def __init__(self, stocks: List):
        self.stocks = stocks
        self.stocks_prices_url = 'https://www.nasdaq.com/symbol/{stock}/historical'
        self.insider_trades_url = 'https://www.nasdaq.com/symbol/{stock}/insider-trades?page={n}'

    def get_prices_urls(self) -> List:
        """Возвращает urls страниц с ценами акций

        Return:
            List
        """
        prices_urls = [(stock.lower(), self.stocks_prices_url.format(stock=stock.lower()))
                       for stock in self.stocks]
        return prices_urls

    def get_trades_urls(self) -> List:
        """Возвращает urls страниц с данными о продажах акций владельцами компаний

        Return:
            List
        """
        page_numbers = list(range(1, 11))
        pages_stocks = sorted(list(itertools.product(page_numbers, self.stocks)), key=lambda x: x[1])
        trades_urls = [(stock.lower(), self.insider_trades_url.format(stock=stock.lower(), n=n))
                       for (n, stock) in pages_stocks]
        return trades_urls

    def get_html_content(self, url: str) -> BeautifulSoup:
        """Получает содержимое страницы

        Args:
            url (str): URL страницы

        Returns:
            BeautifulSoup
        """
        html = requests.get(url)
        content = BeautifulSoup(html.content, 'lxml')
        return content

    def get_or_create_stock(self, content: BeautifulSoup, stock: str) -> Stock:
        """Создает запись с информацией об акции в БД или отдает существующую

        Args:
            content (BeautifulSoup): HTML content
            stock (str): Название акции

        Returns:
            Stock object
        """
        # get company name from title
        title = content.find('h1').text
        for _ in ('Common Stock Historical Stock Prices', 'Capital Stock Historical Stock Prices'):
            title = title.replace(_, '').strip()

        stock, _ = Stock.objects.update_or_create(name=stock, defaults={'company_name': title})
        return stock

    def get_stock_prices(self, stock_and_url: Tuple):
        """Получает цены для заданной акции и сохраняет в БД

        Args:
            stock_and_url (Tuple): Название акции и url страницы
        """
        stock, url = stock_and_url
        content = self.get_html_content(url)
        table = content.select('.genTable > div > table > tbody > tr')
        stock = self.get_or_create_stock(content, stock)

        for row in table:
            date_or_time = row.select('td')[0].text.strip()
            if date_or_time:
                try:
                    date = datetime.strptime(date_or_time, '%m/%d/%Y')
                except ValueError:
                    time = datetime.strptime(date_or_time, '%H:%M')
                    date = datetime.now().replace(hour=time.hour, minute=time.minute)
                opn = row.select('td')[1].text.strip().replace(',', '')
                high = row.select('td')[2].text.strip().replace(',', '')
                low = row.select('td')[3].text.strip().replace(',', '')
                close = row.select('td')[4].text.strip().replace(',', '')
                volume = row.select('td')[5].text.strip().replace(',', '')

                price, _ = Price.objects.get_or_create(
                    stock=stock, date=timezone.make_aware(date, timezone.get_default_timezone()),
                    open=opn, high=high, low=low, close=close, volume=volume
                )

    def get_insider_trades(self, stock_and_url: Tuple):
        """Получает данные о торговле заданной акцией на заданной странице, а затем сохраняет
         информацию в БД

        Args:
            stock_and_url (Tuple): Название акции и url страницы
        """
        stock, url = stock_and_url
        content = self.get_html_content(url)
        table = content.select('.genTable > table > tr')
        stock, _ = Stock.objects.get_or_create(name=stock)

        for row in table:
            insider_name = row.select('td')[0].text.strip()
            relation = row.select('td')[1].text.strip()
            last_date = datetime.strptime(row.select('td')[2].text.strip(), '%m/%d/%Y')
            transaction_type = row.select('td')[3].text.strip()
            owner_type = row.select('td')[4].text.strip()
            shares_traded = row.select('td')[5].text.strip().replace(',', '')
            last_price = row.select('td')[6].text.strip().replace(',', '')
            shares_held = row.select('td')[7].text.strip().replace(',', '')

            insider, _ = Insider.objects.get_or_create(full_name=insider_name)
            relation, _ = Relation.objects.get_or_create(
                position=getattr(Relation.POSITIONS, relation.upper()), stock=stock,
                insider=insider
            )
            trade, _ = Trade.objects.get_or_create(
                insider_relation=relation, last_date=last_date, transaction_type=transaction_type,
                owner_type=getattr(Trade.OWNER_TYPES, owner_type.upper()),
                shares_traded=shares_traded, shares_held=shares_held,
                last_price=last_price if last_price != '' else None,
            )
