from math import trunc

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Trip(models.Model):           # is a Board
    destination = models.CharField(max_length=255)      #maybe change that to: slug = models.SlugField(unique=True, max_length=255)
    trip_members = models.JSONField(default=list)
    start_date = models.DateTimeField()
    start_time = models.TimeField()
    end_date = models.DateTimeField()
    end_time = models.TimeField()
    # owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    # is_public = models.BooleanField(default=False)
    # budget = models.ForeignKey

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date must be before end date")

    def get_duration_days(self):
        return (self.end_date - self.start_date).days

    def __str__(self) -> str:
        return self.destination

# stores the attraction that user wants to visit  within a trip in a specific column-day
class Column(models.Model):
    trip_id = models.ForeignKey(Trip, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Day')
    position = models.PositiveBigIntegerField()      # a numeric field to identify where on the board it would be shown

    class Meta:
        unique_together = ('trip_id', 'position')
        ordering = ['position']

    def __str__(self) -> str:
        return self.title

# A user can add Attraction to a column on the trip-board
class Attraction(models.Model):         # is a trello card
    CATEGORY_CHOICES = [
        ('museum', 'Museum'),
        ('landmark', 'Landmark'),
        ('park', 'Park'),
        ('palace', 'Palace'),
        ('restaurant', 'Restaurant'),
        ('gallery', 'Gallery'),
        ('church', 'Church'),
        ('other', 'Other')
    ]
    column_id = models.ForeignKey(Column, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    location = models.CharField(max_length=50)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='other')
    # maybe it's better to create a separate model 'attraction_attachment' for extra fields [id, attraction_id, uploaded_date, filename, file_location]
    mapUrl = models.URLField(blank=True, null=True)
    ticket = models.URLField(blank=True)                              # or file, to be able to accept all images, urls, or pdfs
    date = models.DateTimeField()
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    visited =models.BooleanField()

    def clean(self):
        if self.cost < 0:
            raise ValidationError("Cost cannot be negative")
   
    def __str__(self) -> str:
        return self.title


class VisitedAttraction(models.Model):
    attraction_id = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])
    images = models.FileField(upload_to='visited_attractions/', null=True, blank=True, help_text='Upload images from your visit')
    moment = models.TextField()                              # experience description, a funny,silly,awkward moment to remember
    reviewed_at = models.DateTimeField()
    actualCost = models.DecimalField(max_digits=6, decimal_places=2)


class Post(models.Model):
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    content = models.TextField()
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    picture = models.ImageField(upload_to='posts/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            unique_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}{counter}'
                counter += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)