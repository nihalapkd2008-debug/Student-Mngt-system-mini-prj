from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    class_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    admission_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.class_name}"