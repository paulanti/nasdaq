from itertools import repeat
from multiprocessing.pool import ThreadPool
from typing import List

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
        threads (int): Количество потоков для парсинга
    """

    def __init__(self, threads: int):
        self.threads = threads
        self.stocks_prices_url = 'https://www.nasdaq.com/{stock}/historical'
        self.insider_trades_url = 'https://www.nasdaq.com/symbol/{stock}/insider-trades'

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

        # get_or_create
        stock, _ = Stock.objects.get_or_create(name=stock, company_name=title)
        return stock

    def get_stock_prices(self, stock: str):
        """Получает цены для заданной акции и сохраняет в БД

        Args:
            stock (str): Название акции
        """
        url = self.stocks_prices_url.format(stock=stock)
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
                    date = timezone.now().replace(hour=time.hour, minute=time.minute)
                opn = row.select('td')[1].text.strip().replace(',', '')
                high = row.select('td')[2].text.strip().replace(',', '')
                low = row.select('td')[3].text.strip().replace(',', '')
                close = row.select('td')[4].text.strip().replace(',', '')
                volume = row.select('td')[5].text.strip().replace(',', '')

                price, _ = Price.objects.get_or_create(
                    stock=stock, date=timezone.make_aware(date, timezone.get_default_timezone()),
                    open=opn, high=high, low=low, close=close, volume=volume
                )

    def get_insider_trades_page_numbers(self, content: BeautifulSoup) -> List:
        """Получет номер последней страницы и отдает список с номерами страниц, которые нужно
        спарсить

        Args:
            content (BeautifulSoup): HTML content

        Returns:
            List
        """
        # get last page number
        last_page_link = content.find(id='quotes_content_left_lb_LastPage').get('href')
        last_page_number = int(last_page_link.split('=')[-1])
        page_numbers = list(range(1, last_page_number + 1 if last_page_number < 10 else 11))
        return page_numbers

    def get_insider_trades(self, stock: str):
        """Получает первую страницу с данными о торговле заданной акцией владельцев компании и
        вызывает метод парсинга для этой и последующих страниц

        Args:
            stock (str): Название акции
        """
        url = self.insider_trades_url.format(stock=stock)
        content = self.get_html_content(url)
        stock = Stock.objects.get(name=stock)
        page_numbers = self.get_insider_trades_page_numbers(content)
        page_numbers_with_stock = zip(page_numbers, repeat(stock))
        with ThreadPool(self.threads) as pool:
            pool.starmap(self.save_insider_trades, page_numbers_with_stock)

    def save_insider_trades(self, n: int, stock: Stock):
        """Получает данные о торговле заданной акцией на заданной странице, а затем сохраняет
         информацию в БД

        Args:
            n (int): Номер страницы
            stock (str): Название акции
        """
        url = f'{self.insider_trades_url.format(stock=stock.name.lower())}?page={n}/'
        content = self.get_html_content(url)
        table = content.select('.genTable > table > tr')

        for row in table:
            insider_name = row.select('td')[0].text.strip()
            relation = row.select('td')[1].text.strip()
            last_date = datetime.strptime(row.select('td')[2].text.strip(), '%m/%d/%Y')
            transaction_type = row.select('td')[3].text.strip()
            owner_type = row.select('td')[4].text.strip()
            shares_traded = row.select('td')[5].text.strip().replace(',', '')
            last_price = row.select('td')[6].text.strip().replace(',', '')
            shares_held = row.select('td')[7].text.strip().replace(',', '')

            # get_or_create
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
