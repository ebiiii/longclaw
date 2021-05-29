from rest_framework import serializers

from longclaw.coupons.models import Coupon, BasketCoupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ["value_absolute", "value_percent", "validity_start", "validity_end", "usage_max"]

    def create(self, validated_data):

        coupon = Coupon.objects.filter(code=validated_data['code']).first()
        if coupon and coupon.is_valid():
            basket_coupon, created = BasketCoupon.objects.get_or_create(
                basket_id=self.context.get('basket_id'),
                defaults={"coupon": coupon},
            )
            if not created:
                raise serializers.ValidationError(_("Basket has already a coupon"))

        else:
            raise serializers.ValidationError(_("Coupon code invalid"))

        return coupon
