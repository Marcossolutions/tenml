from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    category_name = models.CharField(max_length=100, unique= True)
    slug = models.SlugField(max_length=100,unique= True, blank=True)
    is_listed = models.BooleanField(default=True)
    category_image = models.ImageField(upload_to= "category_image/",default="category_image/default.png")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super(Category,self).save(*args, **kwargs)
    
    def __str__(self) :
        return self.category_name
    
    class Meta:
        
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
