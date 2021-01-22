"""
カレンダー画面のプランの設定．
"""

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from ..models import PlanModel, SettingPlanModel, BookModel, WeekdayDefaultModel
from django.views.generic import DeleteView
from django.urls import reverse_lazy, reverse


class DETAIL:
    
    def __init__(self, request, month, date):
        self.username = request.user.get_username()
        self.month = month
        self.date = date
        
    def make_booked_people_name_list(self, object_list):
        #予約者の抽出
        booked_people_name_list = []
        for item in object_list:
            booked_people_name_str = item.booked_people_name
            booked_people_name_str2 = ""
            for booked_people_name in booked_people_name_str.split():
                booked_people_name_str2 += '　' + booked_people_name + ','
            booked_people_name_str2 = booked_people_name_str2[1:-1] #無駄な文字の削除
            booked_people_name_list.append(booked_people_name_str2)
        return booked_people_name_list
    
    def make_zip_list(self, object_list, plan_model_list, booked_people_name_list):
        #3つのリストをzipでまとめ，時間順にsortする
        time_list = [item.time for item in object_list] #並び替えの処理
        try:
            object_plan_name_list = sorted(zip(time_list, object_list, plan_model_list, booked_people_name_list))
            error = ''
        except:
            object_plan_name_list = zip(time_list, object_list, plan_model_list, booked_people_name_list)
            error = '時間が重複しています．'
        return object_plan_name_list, error
    
    def get_context_data(self):
        object_list = list(PlanModel.objects.filter(date=self.date).order_by('time'))
        plan_model_list = list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in object_list)
        booked_people_name_list = self.make_booked_people_name_list(object_list)
        (object_plan_name_list, error) = self.make_zip_list(object_list, plan_model_list, booked_people_name_list)
        context = {
            'month_num': self.month,
            'date': self.date,
            'object_plan_name_list': object_plan_name_list,
            'error': error,
        }
        return context
    
#管理者用のプラン詳細確認
@login_required
def detail_admin_func(request, month, date):
    a = DETAIL(request, month, date)
    context = a.get_context_data()
    return render(request, 'detail_admin.html', context)


class PLAN_UPDATE:
        
    def __init__(self, request, month, date, pk):
        self.request = request
        self.month = month
        self.date = date
        self.pk = pk
        self.item = PlanModel.objects.get(pk=self.pk)
        self.booked_people_name_list = self.item.booked_people_name.split()
        #入力値
        self.last_name = ""
        self.first_name = ""
        self.cancel_name = ""
        self.add_booked_people = ""
        self.time = ""
        self.location = ""
        self.max_book = 0
    
    def get_forms(self):
        self.last_name = self.request.POST['last_name'].replace('　', '').replace(' ', '') #空白削除
        self.first_name = self.request.POST['first_name'].replace('　', '').replace(' ', '') #空白削除
        self.add_booked_people = self.last_name + self.first_name
        self.cancel_name = self.request.POST['cancel_name']
        time1 = self.request.POST["time1"]
        time1_5 = self.request.POST["time1-5"]
        time2 = self.request.POST["time2"]
        time2_5 = self.request.POST["time2-5"]
        self.time = time1 + ":" + time1_5 + "-" + time2 + ":" + time2_5
        self.location = self.request.POST['location']
        self.max_book = int(self.request.POST['max_book'])
    
    def delete_book_model(self, cancel_people):
        book_model = BookModel.objects.get(user=cancel_people)
        book_model_plan = book_model.plan.split()
        book_model_plan.remove(str(self.pk))
        book_model_plan_2 = ''
        for plan in book_model_plan:
            book_model_plan_2 += plan + ' '
        book_model.plan = book_model_plan_2
        book_model.save()
    
    def get_cancel(self):
        #キャンセルの処理
        booked_people_list = self.item.booked_people.split()
        if self.cancel_name in self.booked_people_name_list:
            index_num = self.booked_people_name_list.index(self.cancel_name)
            cancel_people = booked_people_list[index_num]
            booked_people_list.pop(index_num)
            self.booked_people_name_list.pop(index_num)
            booked_people_str = ''
            booked_people_name_str = ''
            for booked_people in booked_people_list:
                booked_people_str += booked_people + ' '
            for booked_people_name in self.booked_people_name_list:
                booked_people_name_str += booked_people_name + ' '
            self.item.booked_people = booked_people_str
            self.item.booked_people_name = booked_people_name_str
            self.item.number_of_people = len(booked_people_list)
            self.item.save()
            #ブックモデルの予約番号の削除
            try: #anonimous用
                self.delete_book_model(cancel_people)
            except:
                pass
    
    def add_book(self):
        #名前からユーザー名を取得
        booked_user = list(User.objects.filter(last_name=self.last_name).filter(first_name=self.first_name))
        if booked_user != []:
            booked_people = self.item.booked_people
            booked_people += ' ' + booked_user[0].username + ' '
            try:
                book_model = BookModel.objects.get(user=booked_user[0].username)
                if book_model.plan == None:
                    book_model_plan = ''
                else:
                    book_model_plan = book_model.plan
                book_model_plan += ' ' + str(self.pk) + ' '
                book_model.plan = book_model_plan
                book_model.save()
            except:
                pass
        else:
            booked_people = self.item.booked_people
            booked_people += ' ' + 'anonumous' + ' ' #anonumousは電話予約された場合の人
        booked_people_name = self.item.booked_people_name
        booked_people_name += ' ' + self.add_booked_people + ' '
        #記録
        self.item.number_of_people = len(booked_people.split())
        self.item.booked_people = booked_people
        self.item.booked_people_name = booked_people_name
        self.item.save()
    
    def get_context_data(self, error):
        context = {
            'month_num': self.month,
            'item': self.item,
            'booked_people_name_list': enumerate(self.booked_people_name_list),
            'people_num': len(self.booked_people_name_list),
            'first_time': self.item.time[:self.item.time.index(':')], #始めの時間
            'first_half_time': self.item.time[self.item.time.index(':') + 1: self.item.time.index('-')],
            'last_time': self.item.time[self.item.time.index('-') + 1: self.item.time.index(':', 5)], #終わりの時間
            'last_half_time': self.item.time[self.item.time.index(':', 5) + 1:],
            'setting_plan_model': SettingPlanModel.objects.all(),
            'error': error,
        }
        return context
        
    def get_post(self):
        #request.method=="POST"のとき
        self.get_forms()
        if self.cancel_name != '': #キャンセルする人がいるとき
            self.get_cancel()
        if self.add_booked_people != '': #予約追加の人がいるとき
            if self.add_booked_people not in self.item.booked_people_name.split():
                self.add_book()
            else:
                error = '入力された追加の予約者は既に予約されています．'
                context = self.get_context_data(error)
                return render(self.request, 'plan_update.html', context)
        self.item.time = self.time
        self.item.location = self.location
        self.item.max_book = self.max_book
        self.item.save()
        
#プランの編集
@login_required
def plan_update(request, month, date, pk):
    a = PLAN_UPDATE(request, month, date, pk)
    if request.method == "POST": #入力された時の処理
        a.get_post()
        return redirect('detail', month, a.item.date)
    error = ""
    context = a.get_context_data(error)
    return render(request, 'plan_update.html', context)


#カレンダーの予約の削除
class PlanDelete(DeleteView):
    template_name = 'plan_delete.html'
    model = PlanModel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = PlanModel.objects.get(pk=self.kwargs['pk'])
        context['date'] = self.kwargs['date']
        context['month_num'] = self.kwargs['month']
        context['plan'] = SettingPlanModel.objects.get(plan_num=item.plan_num)
        return context
    
    def get_success_url(self):
        return reverse('detail', kwargs={'month': self.kwargs['month'], 'date': self.object.date})