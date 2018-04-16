from rest_framework import serializers

from ..models import Stock, Price, Trade


class StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stock
        fields = ('name', 'company_name')


class PriceSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()

    class Meta:
        model = Price
        fields = ('stock', 'date', 'open', 'high', 'low', 'close', 'volume')

    def get_stock(self, obj):
        return obj.stock.name


class TradeSerializer(serializers.ModelSerializer):
    insider = serializers.SerializerMethodField()
    relation = serializers.SerializerMethodField()

    class Meta:
        model = Trade
        fields = ('insider', 'relation', 'last_date', 'transaction_type', 'owner_type',
                  'shares_traded', 'last_price', 'shares_held')

    def get_insider(self, obj):
        return obj.insider_relation.insider.full_name

    def get_relation(self, obj):
        return obj.insider_relation.get_position_display()


class InsiderTradesSerializer(TradeSerializer):
    company = serializers.SerializerMethodField()

    class Meta(TradeSerializer.Meta):
        fields = ('company',) + TradeSerializer.Meta.fields[1:]

    def get_company(self, obj):
        return obj.insider_relation.stock.name
