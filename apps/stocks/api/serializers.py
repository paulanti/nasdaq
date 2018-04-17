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


class PriceAnalyticsSerializer(PriceSerializer):
    delta_open = serializers.SerializerMethodField()
    delta_high = serializers.SerializerMethodField()
    delta_low = serializers.SerializerMethodField()
    delta_close = serializers.SerializerMethodField()
    delta_volume = serializers.SerializerMethodField()

    class Meta(PriceSerializer.Meta):
        fields = PriceSerializer.Meta.fields + ('delta_open', 'delta_high', 'delta_low',
                                                'delta_close', 'delta_volume')

    def get_delta_open(self, obj):
        return obj.delta_open

    def get_delta_high(self, obj):
        return obj.delta_high

    def get_delta_low(self, obj):
        return obj.delta_low

    def get_delta_close(self, obj):
        return obj.delta_close

    def get_delta_volume(self, obj):
        return obj.delta_volume
