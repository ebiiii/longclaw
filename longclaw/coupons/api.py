from rest_framework import viewsets
from longclaw.basket.utils import basket_id

from .models import Coupon, BasketCoupon
from .serializers import CouponSerializer


class CouponViewSet(viewsets.ModelViewSet):
    """
    Create, list and delete Coupon for the related basket
    """
    serializer_class = CouponSerializer

    def get_queryset(self):
        bid = basket_id(self.request)
        return Coupon.objects.filter(usages__basket_id=bid)

    def get_object(self):
        bid = basket_id(self.request)
        return BasketCoupon.objects.filter(basket_id=bid).first()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["basket_id"] = basket_id(self.request)
        return context
