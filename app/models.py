from django.db import models

class Item(models.Model):
    category = models.CharField(max_length=255)
    subcategory = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    amount = models.CharField(max_length=500)
 
    def __str__(self) -> str:
        return self.name


class Trip(models.Model):
    destination = models.CharField(max_length=255)
    duration = models.PositiveBigIntegerField()
    company = models.CharField(max_length=500)
    # budget = models.ForeignKey

    def __str__(self) -> str:
        return self.destination


class Attraction(models.Model):
    title = models.CharField(max_length=60)
    location = models.CharField(max_length=50)
    category = models.CharField(max_length=40)              # museum|landmark|park|palace|restaurant|gallery|church
    mapUrl = models.URLField()
    ticket = models.URLField()                              # or file, to be able to accept all images, urls, or pdfs 
    date = models.DateTimeField()
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    visited =models.BooleanField()
   
    def __str__(self) -> str:
        return self.title
    
class VisitedAttraction(models.Model):
    attractionTitle = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    actualCost = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()                         # experience description
    images = models.DateField()
    moment = models.TextField()                              # a funny,silly,akward moment to remember

    # this displays the rating of the attraction based on company's trip (people that were included)
    def display_rating(self) -> float:
        return Rating.objects.filter(attraction=self).aggregate(Avg("rating"))["rating_ang"] or 0
    
    def __str__(self) -> str:
        return self.title


class Rating(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    attraction = models.ForeignKey(VisitedAttraction, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.attraction.header}: {self.rating}"