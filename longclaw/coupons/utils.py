from longclaw.coupons.models import BasketCoupon


def get_valid_coupon(basket_id=None):
    """Return the coupon if any and if valid
    """
    basket_coupon = BasketCoupon.objects.filter(basket_id=basket_id).first()
    if basket_coupon and basket_coupon.coupon.is_valid():
        return basket_coupon.coupon
