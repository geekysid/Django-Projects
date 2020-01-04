from django.db import models

# Create your models here.

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