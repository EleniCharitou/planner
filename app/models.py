from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Trip(models.Model):           # is a Board
    destination = models.CharField(max_length=255)
    duration = models.PositiveBigIntegerField()
    trip_members = models.CharField(max_length=500)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField()
    # budget = models.ForeignKey

    def __str__(self) -> str:
        return self.destination

# stores the attraction that user wants to visit  within a trip in a specific column-day
class Column(models.Model):
    trip_id = models.ForeignKey(Trip, on_delete=models.CASCADE)
    day = models.CharField(max_length=255)
    position = models.PositiveBigIntegerField()      # a numeric field to identify where on the board it would be shown

    def __str__(self) -> str:
        return self.day

# A user can add Attraction to a column on the trip-board
class Attraction(models.Model):         # is a trello card
    column_id = models.ForeignKey(Column, on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField()
    title = models.CharField(max_length=60)
    location = models.CharField(max_length=50)
    category = models.CharField(max_length=40)              # museum|landmark|park|palace|restaurant|gallery|church
    # maybe it's better to create a separate model 'attraction_attachment' for extra fields [id, attraction_id, uploaded_date, filename, file_location]
    mapUrl = models.URLField()
    ticket = models.URLField()                              # or file, to be able to accept all images, urls, or pdfs 
    date = models.DateTimeField()
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    visited =models.BooleanField()
   
    def __str__(self) -> str:
        return self.title


class VisitedAttraction(models.Model):
    attraction_id = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])
    images = models.TextField()
    moment = models.TextField()                              # experience description, a funny,silly,awkward moment to remember
    reviewed_at = models.DateTimeField()
    actualCost = models.DecimalField(max_digits=6, decimal_places=2)