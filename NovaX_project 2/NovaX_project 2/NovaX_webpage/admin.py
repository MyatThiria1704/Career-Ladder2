from django.contrib import admin
from .models import CareerSurvey, PublicUniversity, PrivateCollege

@admin.register(CareerSurvey)
class CareerSurveyAdmin(admin.ModelAdmin):
    list_display = ('category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('category',)
    readonly_fields = ('created_at', 'responses')

@admin.register(PublicUniversity)
class PublicUniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'location', 'established')
    search_fields = ('name', 'location', 'abbreviation')
    list_filter = ('location',)
    

@admin.register(PrivateCollege)
class PublicUniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'location', 'established')
    search_fields = ('name', 'location', 'abbreviation')
    list_filter = ('location',)