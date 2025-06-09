from decimal import Decimal
from django.db.models import ExpressionWrapper, F, DecimalField


def discount_expression_wrapper(factor: Decimal):
    return ExpressionWrapper(
        F("unit_price") * factor,
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
