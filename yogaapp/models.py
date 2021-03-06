from django.db import models

# ユーザー別の予約したプランの記録
class BookModel(models.Model):
    user = models.CharField('ユーザー名', max_length=100)
    plan = models.CharField('プラン', max_length=1000, default='', null=True, blank=True)
    time_of_cancel = models.IntegerField("キャンセル回数", default=0)
    
    def __str__(self):
        return str(self.user)
    
# 日付別予約人数管理
class PlanModel(models.Model):
    date = models.DateField('日付', null=True)
    month = models.CharField('年月', max_length=10, default=0)
    plan = models.CharField('プラン', max_length=100, default=0)
    short_plan_name = models.CharField('短縮プラン名', max_length=100, default=0)
    number_of_people = models.IntegerField('プランの予約人数', null=True, blank=True, default=0)
    booked_people = models.TextField('プランの予約者', default='', null=True, blank=True)
    booked_people_name = models.TextField('プランの予約者の名前', default='', null=True, blank=True)
    time = models.CharField('時間', max_length=50, default='10～11')
    location = models.CharField('場所', max_length=50, default='スタジオ')
    max_book = models.IntegerField('最大予約人数', default=7)
    plan_num = models.IntegerField('モデルナンバー', default=0)
    
    def __str__(self):
        return str(self.date.strftime('%y-%m-%d')) + '/' + str(self.time)
    
    
# プランの設定
class SettingPlanModel(models.Model):
    name = models.CharField('プラン名', max_length=30)
    short_plan_name = models.CharField('短縮プラン名', max_length=100, default=0)
    price = models.IntegerField('料金', default=500)
    location = models.CharField('場所', max_length=50)
    max_book = models.IntegerField('最大予約人数', default=7)
    memo = models.TextField('メモ', null=True, blank=True)
    image = models.ImageField('画像', null=True, blank=True)
    plan_num = models.IntegerField('モデルナンバー', default=0)
    
    def __str__(self):
        return str(self.name)
    
#お知らせ
class NoteModel(models.Model):
    memo = models.TextField('お知らせ', null=True, blank=True)
    num = models.IntegerField('ナンバー', default=0)
    monday = models.IntegerField('月曜日', default=0) #0は非表示1は表示
    
#曜日別デフォルト設定
class WeekdayDefaultModel(models.Model):
    weekday = models.CharField('曜日', max_length=100, default='')
    plan = models.CharField('プラン', max_length=100, default=0)
    time = models.CharField('時間', max_length=50, default='')
    location = models.CharField('場所', max_length=50, default='スタジオ')
    max_book = models.IntegerField('最大予約人数', default=7)
    plan_num = models.IntegerField('モデルナンバー', default=0)
    
    def __str__(self):
        return self.weekday
    
