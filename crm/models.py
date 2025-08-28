from django.db import models

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True )

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):

        self.total_amount = sum(p.price  for p in self.product.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.customer.name}"

