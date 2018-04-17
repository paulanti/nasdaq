from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from model_utils import Choices

from .querysets import PriceQuerySet


class Stock(models.Model):
    name = models.CharField(
        max_length=10,
        unique=True
    )

    company_name = models.CharField(
        max_length=255,
        default='',
        blank=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('stocks:prices', kwargs={'name': self.name})


class Price(models.Model):
    stock = models.ForeignKey(
        to=Stock,
        on_delete=models.CASCADE,
        related_name='prices'
    )

    date = models.DateTimeField()

    open = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0
    )

    high = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0
    )

    low = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0
    )

    close = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0
    )

    volume = models.IntegerField(
        default=0
    )

    objects = PriceQuerySet.as_manager()

    def __str__(self):
        return f'{self.stock.name} ({self.date.strftime("%m/%d/%Y")})'


class Insider(models.Model):
    full_name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.full_name)
        super().save(*args, **kwargs)


class Relation(models.Model):
    POSITIONS = Choices(
        (0, 'OFFICER', 'Officer'),
        (1, 'DIRECTOR', 'Director')
    )

    position = models.PositiveSmallIntegerField(
        choices=POSITIONS,
        default=POSITIONS.OFFICER
    )

    stock = models.ForeignKey(
        to=Stock,
        on_delete=models.CASCADE
    )

    insider = models.ForeignKey(
        to=Insider,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.insider} {self.get_position_display()} of {self.stock.company_name}'

    class Meta:
        default_related_name = 'relations'


class Trade(models.Model):
    OWNER_TYPES = Choices(
        (0, 'DIRECT', 'direct'),
        (1, 'INDIRECT', 'indirect'),
    )

    insider_relation = models.ForeignKey(
        to=Relation,
        on_delete=models.CASCADE,
        related_name='trades'
    )

    last_date = models.DateField()

    transaction_type = models.CharField(
        max_length=255
    )

    owner_type = models.PositiveSmallIntegerField(
        choices=OWNER_TYPES,
        default=OWNER_TYPES.DIRECT
    )

    shares_traded = models.IntegerField(
        default=0
    )

    last_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )

    shares_held = models.IntegerField(
        default=0
    )

    class Meta:
        ordering = ('last_date', 'insider_relation__insider__full_name')
