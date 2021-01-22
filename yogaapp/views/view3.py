"""
顧客用画面の実装．
予約確定画面，予約確認画面，アクセス，情報画面の機能を実装．
"""

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
import calendar
from ..models import PlanModel, SettingPlanModel, BookModel

class CONFIRM:
    
    def __init__(self, request, month, date):
        self.username = request.user.get_username()
        self.month = month
        self.date = date
        
    def make_weekday(self): #曜日を取得
        weekday_d = {0:'月', 1:'火', 2:'水', 3:'木', 4:'金', 5:'土', 6:'日'}
        weekday = weekday_d[datetime.datetime.strptime(self.date, '%Y-%m-%d').weekday()]
        return weekday
    
    def make_object_list(self): #object_listの取得
        return list(PlanModel.objects.filter(date=self.date))
    
    def make_plan_model_list(self, object_list): #プランモデルの取得
        return list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in object_list)
    
    def make_error_booked(self, object_list):
        #既に予約している人手はないかの確認
        error_booked = []
        for i in range(len(object_list)):
            booked_people_list = object_list[i].booked_people.split()
            if self.username in booked_people_list:
                error_booked.append(1) #予約済
            else:
                error_booked.append(0)
        return error_booked
    
    def make_zip_list(self, object_list, plan_model_list, error_booked):
        #3つのリストをzipでまとめ，時間順にsortする
        time_list = [item.time for item in object_list]#並び替え処理
        try: #同じ時間がある時バグが生じる
            object_plan_error_list = sorted(zip(time_list, object_list, plan_model_list, error_booked))
        except:
            object_plan_error_list = zip(time_list, object_list, plan_model_list, error_booked)
        return object_plan_error_list
    
    def get_context_data(self): #contextデータを作成して返す．
        weekday = self.make_weekday()
        object_list = self.make_object_list()
        plan_model_list = self.make_plan_model_list(object_list)
        error_booked = self.make_error_booked(object_list)
        object_plan_error_list = self.make_zip_list(object_list, plan_model_list, error_booked)
        context = {
            'month0': self.month,
            'month': self.date[5:7],
            'day': self.date[8:],
            'object_plan_error_list': object_plan_error_list,
            'weekday': weekday
        }
        return context

#プラン選択画面
@login_required
def confirmfunc(request, month, date):
    a = CONFIRM(request, month, date)
    context = a.get_context_data()
    return render(request, 'confirm.html', context)


class GET_CONFIRM:
    
    def __init__(self, request, month, date, pk):
        self.username = request.user.get_username()
        self.month = month
        self.date = date
        self.pk = pk
        self.name = User.objects.get(username=self.username).last_name + User.objects.get(username=self.username).first_name
        
    def make_objects(self):
        return PlanModel.objects.get(pk=self.pk)
    
    def save_planmodel(self, objects):
        #PlanModelに予約者の名前を記録
        objects.booked_people += self.username + ' ' 
        objects.booked_people_name += self.name + ' '
        booked_people_list = objects.booked_people.split()
        objects.number_of_people = len(booked_people_list)
        objects.save()
    
    def save_bookmodel(self):
        #ユーザー別で予約したプランを記録
        if list(BookModel.objects.filter(user=self.username)) == []:
            user_plan = BookModel.objects.create()
            user_plan.user = self.username
            user_plan.plan = str(self.pk)
        else:
            user_plan = BookModel.objects.filter(user=self.username)[0]
            try:
                user_plan.plan += ' ' + str(self.pk)
            except:
                user_plan.plan = str(self.pk)
        user_plan.save()
    
#planの予約確定処理
@login_required
def get_confirm(request, month, date, pk):
    objects = PlanModel.objects.get(pk=pk)
    a = GET_CONFIRM(request, month, date, pk)
    if a.username in objects.booked_people.split(): #予約者の重複を無くすための処理
        return redirect('book', month)
    else:
        a.save_planmodel(objects)
        a.save_bookmodel() #ユーザー別で予約したプランを記録
    return redirect('confirm', month, date)


class CANCEL:
    
    def __init__(self, request, month, date, pk):
        self.username = request.user.get_username()
        self.month = month
        self.date = date
        self.pk = pk
        self.name = User.objects.get(username=self.username).last_name + User.objects.get(username=self.username).first_name
    
    def make_booked_people_list(self, objects):
        booked_people_list = objects.booked_people.split()
        booked_people_list.remove(self.username)
        return booked_people_list
    
    def make_booked_people_name_list(self, objects):
        booked_people_name_list = objects.booked_people_name.split()
        booked_people_name_list.remove(self.name)
        return booked_people_name_list
    
    def save_planmodel(self, objects, booked_people_list, booked_people_name_list):
        #PlanModelに刻まれているキャンセルユーザーの削除処理
        booked_people_str = ''
        booked_people_name_str = ''
        for booked_people in booked_people_list:
            booked_people_str += booked_people + ' '
        for booked_people_name in booked_people_name_list:
            booked_people_name_str += booked_people_name + ' '
        objects.booked_people = booked_people_str
        objects.booked_people_name = booked_people_name_str
        objects.number_of_people = len(booked_people_list) #予約人数を減らす
        objects.save()
    
    def save_bookmodel(self):
        #ユーザー別で予約したプランの削除
        user_plan = BookModel.objects.filter(user=self.username)[0]
        plan_list = user_plan.plan.split()
        try:
            plan_list.remove(str(self.pk))
        except:
            pass
        plan_str = ''
        for plan in plan_list:
            plan_str += plan + ' '
        #キャンセル回数のカウント
        user_plan.time_of_cancel = user_plan.time_of_cancel + 1
        user_plan.plan = plan_str
        user_plan.save()

#planのキャンセル
@login_required
def cancel_yoga_func(request, month, date, pk, mark):
    objects = PlanModel.objects.get(pk=pk)
    a = CANCEL(request, month, date, pk)
    booked_people_list = a.make_booked_people_list(objects)
    booked_people_name_list = a.make_booked_people_name_list(objects)
    a.save_planmodel(objects, booked_people_list, booked_people_name_list)
    a.save_bookmodel()
    if mark == '0':
        return redirect('confirm', month, date)
    elif mark == "1":
        return redirect('booked_list')


class BOOKED_PLAN:

    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month, today.day)
    
    def __init__(self, username):
        self.username = username
        
    def clean_plan(self):
        #ユーザー別のプランpkの掃除
        book_model = BookModel.objects.get(user=self.username)
        pk_list = book_model.plan.split()
        new_pk_list = []
        for i in range(len(pk_list)):
            PK = int(pk_list[i])
            try:
                DATE = PlanModel.objects.get(pk=PK).date
                booked_people = PlanModel.objects.get(pk=PK).booked_people.split() #プランモデルの方に名前が入っているかの確認
                if (datetime.datetime(DATE.year, DATE.month, DATE.day) - self.today).days >= 0 and self.username in booked_people:
                    new_pk_list.append(str(PK))
            except: #指定pkプランが削除されていた場合のバグ回避
                pass
        #記録
        pk_str = ''
        for p in new_pk_list:
            pk_str += p + ' '
        book_model.plan = pk_str
        book_model.save()
    
    def make_pk_list(self):
        if list(BookModel.objects.filter(user=self.username)) == []:
            user_plan = BookModel.objects.create()
            user_plan.user = self.username
            user_plan.save()
        if BookModel.objects.filter(user=self.username)[0].plan == None:
            pk_list = []
        else:
            pk_list = BookModel.objects.filter(user=self.username)[0].plan.split()
        return pk_list
    
    def make_object_list(self):
        #ユーザーの予約したプランのpkを取得
        object_list = []
        date_list = []
        pk_list = self.make_pk_list()
        for pk in pk_list:
            date_list_2 = str(PlanModel.objects.get(pk=pk).date).split('-')
            #日にちが今日よりも後の物のみ格納
            if (datetime.datetime(int(date_list_2[0]), int(date_list_2[1]), int(date_list_2[2])) - self.today).days >= 0:
                object_list.append(PlanModel.objects.get(pk=pk))
                date_list.append(PlanModel.objects.get(pk=pk).date)
        object_list = sorted(object_list, key = lambda x: (x.date, x.time))
        return object_list
        
    def make_plan_model_list(self, object_list):
        return list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in object_list)
        
    def make_weekday_list(self, object_list):
        #予約したプランのプラン設定の取得
        weekday_d = {0:'月', 1:'火', 2:'水', 3:'木', 4:'金', 5:'土', 6:'日'}
        weekday_list = []
        for item in object_list:
            weekday_list.append(weekday_d[item.date.weekday()])
        return weekday_list
        
    def get_context_data(self):
        object_list = self.make_object_list()
        plan_model_list = self.make_plan_model_list(object_list)
        weekday_list = self.make_weekday_list(object_list)
        context = {
            'object_list': zip(object_list, plan_model_list, weekday_list),
            'check': 0 if object_list == [] else 1,
        }
        return context

#予約確認画面．予約したプランを返す．
@login_required
def booked_list_func(request):
    username = request.user.get_username()
    a = BOOKED_PLAN(username)
    a.clean_plan()
    context = a.get_context_data()
    return render(request, 'booked_list.html', context)


#アクセス画面
@login_required
def access_func(request):
    return render(request, 'access.html')


#インフォメーション画面
@login_required
def info_func(request):
    return render(request, 'info.html')

