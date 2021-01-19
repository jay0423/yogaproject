from django.db import models

# Create your models here.
class BookModel(models.Model):
    user = models.CharField('username', max_length=100)
    
class PlanModel(models.Model):
    date = models.DateField('日付', null=True)
    month = models.CharField('月', max_length=2, default=0)
    plan = models.CharField('プラン1', max_length=30, default=0)
    plan2 = models.CharField('プラン2', max_length=30, default=0)
    number_of_people_1 = models.IntegerField('プラン1の予約人数', null=True, blank=True, default=0)
    number_of_people_2 = models.IntegerField('プラン2の予約人数', null=True, blank=True, default=0)
    booked_people_1 = models.TextField('プラン1の予約者', default='', null=True, blank=True)
    booked_people_2 = models.TextField('プラン2の予約者', default='', null=True, blank=True)
    
    def __str__(self):
        return str(self.date)
    
# class MemoModel(models.Model):
#     yoga