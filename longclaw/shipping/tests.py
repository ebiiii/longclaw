import uuid

from django.test import TestCase
from django.forms.models import model_to_dict
from longclaw.tests.utils import LongclawTestCase, AddressFactory, CountryFactory, ShippingRateFactory, BasketItemFactory
from longclaw.shipping.forms import AddressForm
from longclaw.shipping.utils import get_shipping_cost
from longclaw.shipping.templatetags import longclawshipping_tags
from longclaw.configuration.models import Configuration
from longclaw.basket.utils import basket_id

from .models import ShippingRate


class ShippingTests(LongclawTestCase):
    def setUp(self):
        self.country = CountryFactory()
    def test_create_address(self):
        """
        Test creating an address object via the api
        """
        data = {
            'name': 'Bob Testerson',
            'line_1': 'Bobstreet',
            'city': 'Bobsville',
            'postcode': 'BOB22 2BO',
            'country': self.country.pk
        }
        self.post_test(data, 'longclaw_address_list')

    def test_shipping_cost(self):
        sr = ShippingRateFactory(countries=[self.country])
        result = get_shipping_cost(Configuration(), self.country.pk, sr.name)
        self.assertEqual(result["rate"], sr.rate)

    def test_multiple_shipping_cost(self):
        sr = ShippingRateFactory(countries=[self.country])
        sr2 = ShippingRateFactory(countries=[self.country])
        result = get_shipping_cost(Configuration(), self.country.pk, sr.name)
        self.assertEqual(result["rate"], sr.rate)

    def test_default_shipping_cost(self):
        ls = Configuration(default_shipping_enabled=True)
        result = get_shipping_cost(ls)
        self.assertEqual(ls.default_shipping_rate, result["rate"])


class ShippingBasketTests(LongclawTestCase):
    def setUp(self):
        """Create a basket with things in it
        """
        request = RequestFactory().get('/')
        request.session = {}
        self.bid = basket_id(request)
        self.item = BasketItemFactory(basket_id=bid)
        BasketItemFactory(basket_id=bid)
        
        self.rate1 = ShippingRate.objects.create(
            name='98d17c43-7e20-42bd-b603-a4c83c829c5a',
            rate=99,
            carrier='8717ca67-4691-4dff-96ec-c43cccd15241',
            description='313037e1-644a-4570-808a-f9ba82ecfb34',
            basket_id=bid,
        )
    
    def test_basket_rate(self):
        result = get_shipping_cost(Configuration(), name='98d17c43-7e20-42bd-b603-a4c83c829c5a', basket_id=self.bid)
        self.assertEqual(result["rate"], 99)
        self.assertEqual(result["description"], '313037e1-644a-4570-808a-f9ba82ecfb34')


class AddressFormTest(TestCase):

    def setUp(self):
        self.address = AddressFactory()

    def test_address_form(self):
        form = AddressForm(data=model_to_dict(self.address))
        self.assertTrue(form.is_valid(), form.errors.as_json())

