from django.db import models
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
  category_name = models.CharField(max_length = 40, unique = True)
  parent = models.ForeignKey('self', null = True, blank = True, on_delete = models.CASCADE)

  is_available = models.BooleanField(default = True)

  class Meta:
    verbose_name = 'Category'
    verbose_name_plural = 'categories'


  def save(self, *args, **kwargs):
    self.slug = slugify(self.category_name)
    super(Category, self).save(*args, **kwargs)


  def __str__(self) -> str:
    return self.category_name