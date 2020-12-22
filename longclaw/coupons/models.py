from django.db import models
from django.utils.timezone import now


from wagtail.admin.edit_handlers import FieldPanel


class Coupon(models.Model):
    """
    Coupons are modifiers that can be applied to a basket and order
    """
    code = models.CharField(
        max_length=32,
        unique=True,
    )
    value_absolute = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    value_percent = models.SmallIntegerField(default=0)

    validity_start = models.DateTimeField()
    validity_end = models.DateTimeField(null=True, blank=True)

    usage_max = models.SmallIntegerField(default=0)

    panels = [
        FieldPanel('code'),
        FieldPanel('value_absolute'),
        FieldPanel('value_percent'),
        FieldPanel('validity_start'),
        FieldPanel('validity_end'),
        FieldPanel('usage_max'),
    ]

    def is_valid(self):
        if self.validity_start > now() or (self.validity_end and self.validity_end < now()):
            return False

        if self.usage_max > 0 and self.orders.count() >= self.usage_max:
            return False

        return True

    def __str__(self):
        return self.code


class BasketCoupon(models.Model):
    basket_id = models.CharField(max_length=32, unique=True)
    coupon = models.ForeignKey(Coupon, related_name="usages", on_delete=models.CASCADE)
