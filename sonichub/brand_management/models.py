from django.db import models

class Brand(models.Model):
  brand_name = models.CharField(max_length = 40, null = False, unique = True)
  brand_image = models.ImageField(upload_to= 'brand_images')

  status = models.BooleanField(default = True)


  def __str__(self) -> str:
    return self.brand_name

