try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _

from wagtail import hooks
from wagtail.admin import widgets
from longclaw.utils import ProductVariant

@hooks.register('register_page_listing_buttons')
def product_requests_button(page, page_perms):
    """Renders a 'requests' button on the page index showing the number
    of times the product has been requested.

    Attempts to only show such a button for valid product/variant pages
    """
    # Is this page the 'product' model?
    # It is generally safe to assume either the page will have a 'variants'
    #  member or will be an instance of longclaw.utils.ProductVariant
    if hasattr(page, 'variants') or isinstance(page, ProductVariant):
        yield widgets.PageListingButton(
            _('View Requests'),
            reverse('productrequests_admin', kwargs={'pk': page.id}),
            priority=40
        )
