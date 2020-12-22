from django.conf.urls import url
from longclaw.coupons import api
from longclaw.settings import API_URL_PREFIX

coupon_api = api.CouponViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'delete': 'destroy',
})


urlpatterns = [
    url(API_URL_PREFIX + r'coupons/$',
        coupon_api,
        name='longclaw_coupon_api')
]
