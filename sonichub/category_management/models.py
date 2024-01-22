from django.db import models
from django.utils.text import slugify

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=40, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    minimum_amount = models.CharField(max_length=40, null=True)
    discount = models.IntegerField(null=True)
    expirydate = models.DateField(null=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.category_name
