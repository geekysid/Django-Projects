from django.db import models

# Create your models here.

# Product Model
class Products(models.Model):
    product_id = models.AutoField
    name = models.CharField(max_length=100)
    desc = models.TextField(max_length=2500)
    category = models.CharField(max_length=20, default="")
    date_add = models.DateField()
    price = models.FloatField()
    discount = models.FloatField(default=0.00)
    image = models.ImageField(upload_to="image/shop/", default="")

    def __str__(self):
        return self.name

# Order Model. 
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    address = models.TextField(max_length=300)
    landmark = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=6)
    message = models.CharField(max_length=200)
    paymode = models.CharField(max_length=20)

    def __str__(self):
        return str(self.order_id)

# Ordered_Product Model. This model has couple of Foreign Keys which points to a row in Order Model and Product Model
class Ordered_Product(models.Model):
    order_product_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    discount = models.FloatField()
    price = models.FloatField()
    image = models.CharField(max_length=300)

    def __str__(self):
        return str(f"{self.order_id} - {self.product}")

# Order_Status Model. This model has a Foreign Key which points to a row in Order Model
class Order_Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status_desc = models.TextField()
    remark = models.TextField(default="We will contact you via mail")
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(f"{self.order_id} - {self.status_desc[:20]}...")

