from django.db import models


# Create your models here.

class Book(models.Model):
    book_name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    pages = models.IntegerField(null=True)
    price = models.IntegerField(null=True)

    def __str__(self):
        return self.book_name
