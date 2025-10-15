from django.db import models

class CareerSurvey(models.Model):
    CATEGORY_CHOICES = [
        ('Aptitude test Q', 'Aptitude test'),
        ('Educational test Q', 'Educational test'),
        ('Combined test Q', 'Combined test'),
    ]

    #category = models.CharField(max_length=200, choices=CATEGORY_CHOICES)
    
    category = models.CharField(max_length=200)
    responses = models.JSONField()  # stores answers in JSON format
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


from django.db import models

class PublicUniversity(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    established = models.IntegerField()
    description = models.TextField()
    about = models.TextField()
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class PrivateCollege(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    established = models.IntegerField()
    description = models.TextField()
    about = models.TextField()
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
