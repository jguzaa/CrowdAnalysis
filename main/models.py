from django.contrib.auth.models import User
from django.db import models
from datetime import  datetime
from django.conf import settings
# Create your models here.
# All models will be inherited from Django base model

# each model will map to database's table

# user model
class CrowdDensity(models.Model):
    #define the columns of the database
    user_dashboard_title = models.CharField(max_length=200) # set a fixed field
    user_dashboard_content = models.TextField()
    user_dashboard_published = models.DateTimeField("date published", default=datetime.now)


    # override string method
    def __str__(self):
        return self.user_dashboard_title

# user report model
class GraphCategory(models.Model):
    graph_category = models.CharField(max_length=200)
    category_summary = models.CharField(max_length=200)
    category_slug = models.CharField(max_length=200, default=1) # for the url

    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return  self.graph_category

# video model
class Footage(models.Model):

    video_title = models.CharField(max_length=100)
    upload_date = models.DateTimeField("date uploaded", default=datetime.now)
    video = models.FileField(upload_to='videos/', null=True)

    # override string method
    def __str__(self):
        return self.video_title
