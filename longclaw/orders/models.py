from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from longclaw.settings import PRODUCT_VARIANT_MODEL
from longclaw.shipping.models import Address
from longclaw.coupons.models import Coupon


class Order(models.Model):
    SUBMITTED = 1
    FULFILLED = 2
    CANCELLED = 3
    REFUNDED = 4
    FAILURE = 5
    ACCEPTED = 6
    ORDER_STATUSES = ((SUBMITTED, _('Submitted')),
                      (FULFILLED, _('Fulfilled')),
                      (CANCELLED, _('Cancelled')),
                      (REFUNDED, _('Refunded')),
                      (FAILURE, _('Payment Failed')),
                      (ACCEPTED, _('Payment Succeeded')))
    payment_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ORDER_STATUSES, default=SUBMITTED)
    status_note = models.CharField(max_length=128, blank=True, null=True)

    transaction_id = models.CharField(max_length=256, blank=True, null=True)

    # contact info
    email = models.EmailField(max_length=128, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name="orders", on_delete=models.SET_NULL)

    # shipping info
    shipping_address = models.ForeignKey(
        Address, blank=True, null=True, related_name="orders_shipping_address", on_delete=models.PROTECT)

    # billing info
    billing_address = models.ForeignKey(
        Address, blank=True, null=True, related_name="orders_billing_address", on_delete=models.PROTECT)

    shipping_rate = models.DecimalField(max_digits=12,
                                        decimal_places=2,
                                        blank=True,
                                        null=True)

    coupon = models.ForeignKey(Coupon, blank=True, null=True, related_name="orders", on_delete=models.PROTECT)

    def __str__(self):
        return _("Order #{} - {}").format(self.id, self.email)

    @property
    def total(self):
        """Total cost of the order
        """
        total = 0
        for item in self.items.all():
            total += item.total
        if self.coupon and self.coupon.value_percent:
            total = total - (total * min(self.coupon.value_percent, Decimal("100.0")) / Decimal("100.0"))
        if self.coupon and self.coupon.value_absolute:
            total = max(total - self.coupon.value_absolute, Decimal("0.0"))
        return total

    @property
    def total_items(self):
        """The number of individual items on the order
        """
        return self.items.count()


    def refund(self):
        """Issue a full refund for this order
        """
        from longclaw.utils import GATEWAY
        now = datetime.strftime(datetime.now(), "%b %d %Y %H:%M:%S")
        if GATEWAY.issue_refund(self.transaction_id, self.total):
            self.status = self.REFUNDED
            self.status_note = _("Refunded on {}").format(now)
        else:
            self.status_note = _("Refund failed on {}").format(now)
        self.save()

    def fulfill(self):
        """Mark this order as being fulfilled
        """
        self.status = self.FULFILLED
        self.save()

    def cancel(self, refund=True):
        """Cancel this order, optionally refunding it
        """
        if refund:
            self.refund()
        self.status = self.CANCELLED
        self.save()

class OrderItem(models.Model):
    product = models.ForeignKey(PRODUCT_VARIANT_MODEL, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    keep_price = models.DecimalField(max_digits=12, decimal_places=2)
    keep_title = models.CharField(max_length=255)

    @property
    def total(self):
        return self.quantity * self.keep_price

    def __str__(self):
        return "{} x {}".format(self.quantity, self.keep_title)
