from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from django.utils.translation import ugettext_lazy as _
from longclaw.coupons.models import Coupon


class CouponModelAdmin(ModelAdmin):
    model = Coupon
    menu_label = _('Coupon')
    menu_order = 200
    menu_icon = 'success'
    add_to_settings_menu = False
    exclude_from_explorer = True
    list_display = ('code', 'value_absolute', 'value_percent', 'validity_start', 'validity_end', 'usage_max')


modeladmin_register(CouponModelAdmin)
