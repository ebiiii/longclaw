from django.core.cache import cache
from django.db import models, transaction
from django.dispatch import receiver

from longclaw.basket.signals import basket_modified
from polymorphic.models import PolymorphicModel
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.models import register_snippet

from .signals import address_modified


@register_snippet
class Address(models.Model):
    name = models.CharField(max_length=64)
    line_1 = models.CharField(max_length=128)
    line_2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=64)
    postcode = models.CharField(max_length=10)
    country = models.ForeignKey('shipping.Country', blank=True, null=True, on_delete=models.PROTECT)

    panels = [
        FieldPanel('name'),
        FieldPanel('line_1'),
        FieldPanel('line_2'),
        FieldPanel('city'),
        FieldPanel('postcode'),
        FieldPanel('country')
    ]

    def __str__(self):
        return "{}, {}, {}".format(self.name, self.city, self.country)


@receiver(address_modified)
def clear_address_rates(sender, instance, **kwargs):
    ShippingRate.objects.filter(destination=instance).delete()


class ShippingRateProcessor(PolymorphicModel):
    countries = models.ManyToManyField('shipping.Country')
    
    rates_cache_timeout = 300
    def get_rates(self, settings=None, basket_id=None, destination=None):
        kwargs = dict(settings=settings, basket_id=basket_id, destination=destination)
        key = self.get_rates_cache_key(**kwargs)
        rates = cache.get(key)
        if rates is None:
            with transaction.atomic():
                rates = self._process_rates(**kwargs)
            if rates is not None:
                for rate in rates:
                    rate.basket_id = basket_id
                    rate.destination = destination
                    rate.processor = self
                    rate.save()
                cache.set(key, rates, self.rates_cache_timeout)
        return rates
    
    def get_rates_cache_key(self, **kwargs):
        raise NotImplementedError()
    
    def _get_rates(self, **kwargs):
        raise NotImplementedError()


class ShippingRate(models.Model):
    """
    An individual shipping rate. This can be applied to
    multiple countries.
    """
    name = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique name to refer to this shipping rate by"
    )
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    carrier = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    countries = models.ManyToManyField('shipping.Country')
    basket_id = models.CharField(blank=True, db_index=True, max_length=32)
    destination = models.ForeignKey(Address, blank=True, null=True, on_delete=models.PROTECT)
    processor = models.ForeignKey(ShippingRateProcessor, blank=True, null=True, on_delete=models.PROTECT)

    panels = [
        FieldPanel('name'),
        FieldPanel('rate'),
        FieldPanel('carrier'),
        FieldPanel('description'),
        FieldPanel('countries')
    ]

    def __str__(self):
        return self.name


@receiver(basket_modified)
def clear_basket_rates(sender, basket_id, **kwargs):
    ShippingRate.objects.filter(basket_id=basket_id).delete()


class Country(models.Model):
    """
    International Organization for Standardization (ISO) 3166-1 Country list
    Instance Variables:
    iso -- ISO 3166-1 alpha-2
    name -- Official country names (in all caps) used by the ISO 3166
    display_name -- Country names in title format
    sort_priority -- field that allows for customizing the default ordering
    0 is the default value, and the higher the value the closer to the
    beginning of the list it will be.  An example use case would be you will
    primarily have addresses for one country, so you want that particular
    country to be the first option in an html dropdown box.  To do this, you
    would simply change the value in the json file or alter
    country_grabber.py's priority dictionary and run it to regenerate
    the json
    """
    iso = models.CharField(max_length=2, primary_key=True)
    name_official = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    sort_priority = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('-sort_priority', 'name',)

    def __str__(self):
        """ Return the display form of the country name"""
        return self.name
