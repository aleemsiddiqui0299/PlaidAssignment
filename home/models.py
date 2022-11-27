from django.db import models

# Create your models here.
class Contact(models.Model):
    password = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self) -> str:
        return self.city