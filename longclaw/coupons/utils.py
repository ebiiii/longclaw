from longclaw.coupons.models import BasketCoupon, Coupon


def get_coupon(basket_id=None):
    """Return the coupon if any
    """
    basket_coupon = BasketCoupon.objects.filter(basket_id=basket_id).first()
    if basket_coupon:
        return Coupon.objects.select_for_update().get(pk=basket_coupon.coupon_id)
