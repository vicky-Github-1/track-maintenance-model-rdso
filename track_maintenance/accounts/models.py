from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('engineer', 'Engineer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='engineer') 
    zone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    # zone = models.CharField(max_length=20, choices=[
    #     ('North', 'North'),
    #     ('South', 'South'),
    #     ('East', 'East'),
    #     ('West', 'West'),
    #     ('Central', 'Central'),
    # ])
    # city = models.CharField(max_length=100)
    

    entry_by = models.ForeignKey("self", related_name="entry_created", on_delete=models.SET_NULL, null=True, blank=True)
    modified_by = models.ForeignKey("self", related_name="entry_modified", on_delete=models.SET_NULL, null=True, blank=True)
    delete_by = models.ForeignKey("self", related_name="entry_deleted", on_delete=models.SET_NULL, null=True, blank=True)
    
    entry_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

class PredictionResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
    track_id = models.CharField(max_length=100)
    speed = models.FloatField()
    vibration = models.FloatField()
    temperature = models.FloatField()
    axle_load = models.FloatField()
    # Region= models.CharField(max_length=100)
    prediction_percent = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'engineer'})
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.track_id} - {self.prediction_percent}%"
    
    
