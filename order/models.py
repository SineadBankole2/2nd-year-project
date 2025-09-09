from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from vouchers.models import Voucher
from store.models import Product


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        PAID = "Paid", "Paid"
        SHIPPED = "Shipped", "Shipped"
        CANCELLED = "Cancelled", "Cancelled"
        REFUNDED = "Refunded", "Refunded"

    # Link order to the actual user (optional for guests)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )

    token = models.CharField(max_length=250, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Euro Order Total')
    emailAddress = models.EmailField(max_length=250, blank=True, verbose_name='Email Address')
    created = models.DateTimeField(auto_now_add=True)

    billingName = models.CharField(max_length=250, blank=True)
    billingAddress1 = models.CharField(max_length=250, blank=True)
    billingCity = models.CharField(max_length=250, blank=True)
    billingPostcode = models.CharField(max_length=10, blank=True)
    billingCountry = models.CharField(max_length=200, blank=True)

    shippingName = models.CharField(max_length=250, blank=True)
    shippingAddress1 = models.CharField(max_length=250, blank=True)
    shippingCity = models.CharField(max_length=250, blank=True)
    shippingPostcode = models.CharField(max_length=10, blank=True)
    shippingCountry = models.CharField(max_length=200, blank=True)

    voucher = models.ForeignKey(
        Voucher, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL
    )
    # Store discount as percent (0–100)
    discount = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PAID
    )

    class Meta:
        db_table = 'Order'
        ordering = ['-created']

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    # Legacy text name (kept so old rows still render)
    product = models.CharField(max_length=250)

    # Recommended: link to the Product so we can show image and allow reviews
    product_ref = models.ForeignKey(
        Product, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='order_items'
    )

    quantity = models.IntegerField()
    # Store UNIT price (subtotal is quantity * price)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Euro Price')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        db_table = 'OrderItem'

    def sub_total(self):
        return self.quantity * self.price

    def __str__(self):
        return self.product_ref.name if getattr(self, "product_ref", None) else self.product
