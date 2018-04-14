from django.core import serializers
from django.http import HttpResponse


class JsonResponseMixin:
    """Миксин для возврата данных в формате json
    """
    def render_to_response(self, context, **response_kwargs):
        queryset = self.get_queryset()
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')
