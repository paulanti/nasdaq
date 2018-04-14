from multiprocessing.pool import ThreadPool

from django.core.management import BaseCommand

from apps.stocks.parser import get_stocks_list, NasdaqParser


class Command(BaseCommand):
    help = "Parse Nasdaq.com"
    missing_args_message = "Отсутствует параметр threads"

    def add_arguments(self, parser):
        parser.add_argument('threads', nargs='+', type=int)

    def handle(self, *args, **options):
        threads = options['threads']
        stock_list = get_stocks_list('tickers.txt')
        parser = NasdaqParser(threads[0])
        with ThreadPool(threads[0]) as pool:
            pool.map(parser.get_stock_prices, stock_list)
            pool.map(parser.get_insider_trades, stock_list)
