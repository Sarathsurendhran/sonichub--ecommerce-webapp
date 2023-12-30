from django import forms
from .models import Product_images

class ImageForm(forms.ModelForm):
  class Meta:
    model = Product_images
    fields = ('images',)