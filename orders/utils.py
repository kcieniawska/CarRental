# orders/utils.py
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Możesz także użyć str(obj), jeśli chcesz jako string
        return super().default(obj)
