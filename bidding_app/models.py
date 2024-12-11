from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Project(models.Model):
    project_id = models.CharField(max_length=4)
    project_description = models.CharField(max_length=100)
    project_objective = models.CharField(max_length=100)
    project_deliverables = models.CharField(max_length=100)
    project_skills = models.CharField(max_length=100)
    project_notes = models.CharField(max_length=100)

    def __REPR__(self):
        return self.project_id + "\t" + self.project_notes

class BiddingUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.PROTECT)
    password = models.CharField(max_length=8,default='')
    email = models.EmailField()

class Bids(models.Model):
    bidding_user = models.ForeignKey(BiddingUser,on_delete=models.PROTECT)
    project = models.CharField(max_length=4)
    bid_amt = models.IntegerField(default=0)
