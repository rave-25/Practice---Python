from django.db import models

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=200, null=True)
    requirements = models.CharField(max_length=200, null=True)
    duration = models.IntegerField(null=True)
    totalhours = models.IntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.name

class Leaves(models.Model):
    CATEGORY = (
        ('Vaccation', 'Vaccation'),
        ('Sick', 'Sick'),
        ('Emergency', 'Emergency'),
        ('Others', 'Others'),
    )
    name = models.CharField(max_length=200, null=True)
    category = models.CharField(max_length=200, null=True, choices=CATEGORY) 
    description = models.CharField(max_length=200, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Delivered', 'Delivered')
    )
    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
    rendered = models.IntegerField(null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS)



