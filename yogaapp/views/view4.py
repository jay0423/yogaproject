"""
管理者用画面の設定．
"""

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from ..models import PlanModel, SettingPlanModel, BookModel, NoteModel, WeekdayDefaultModel
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, ListView
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

 
#プランの編集
@login_required
def plan_update(request, month, date, pk):
    item = PlanModel.objects.get(pk=pk)
    setting_plan_model = SettingPlanModel.objects.all()
    #表示処理
    booked_people_name_list = item.booked_people_name.split()
    if request.method == "POST": #入力された時の処理
        last_name = request.POST['last_name'].replace('　', '').replace(' ', '') #空白削除
        first_name = request.POST['first_name'].replace('　', '').replace(' ', '') #空白削除
        cancel_name = request.POST['cancel_name']
        time1 = request.POST["time1"]
        time1_5 = request.POST["time1-5"]
        time2 = request.POST["time2"]
        time2_5 = request.POST["time2-5"]
        time = time1 + ":" + time1_5 + "-" + time2 + ":" + time2_5
        location = request.POST['location']
        max_book = request.POST['max_book']
        if cancel_name != '': #キャンセルする人がいるとき
            booked_people_list = item.booked_people.split()
            booked_people_name_list = item.booked_people_name.split()
            if cancel_name in booked_people_name_list:
                index_num = booked_people_name_list.index(cancel_name)
                cancel_people = booked_people_list[index_num] #633行目以降用
                booked_people_list.pop(index_num)
                booked_people_name_list.pop(index_num)
                booked_people_str = ''
                booked_people_name_str = ''
                for booked_people in booked_people_list:
                    booked_people_str += booked_people + ' '
                for booked_people_name in booked_people_name_list:
                    booked_people_name_str += booked_people_name + ' '
                item.booked_people = booked_people_str
                item.booked_people_name = booked_people_name_str
                item.number_of_people = len(booked_people_list)
                item.save()
                #ブックモデルの予約番号の削除
                try: #anonimous用
                    book_model = BookModel.objects.get(user=cancel_people)
                    book_model_plan = book_model.plan.split()
                    book_model_plan.remove(str(pk))
                    book_model_plan_2 = ''
                    for plan in book_model_plan:
                        book_model_plan_2 += plan + ' '
                    book_model.plan = book_model_plan_2
                    book_model.save()
                except:
                    pass
        add_booked_people = last_name + first_name
        if add_booked_people != '': #予約追加の人がいるとき
            if add_booked_people not in item.booked_people_name.split():
                #名前からユーザー名を取得
                booked_user = list(User.objects.filter(last_name=last_name).filter(first_name=first_name))
                if booked_user != []:
                    booked_people = item.booked_people
                    booked_people += ' ' + booked_user[0].username + ' '
                    try:
                        book_model = BookModel.objects.get(user=booked_user[0].username)
                        if book_model.plan == None:
                            book_model_plan = ''
                        else:
                            book_model_plan = book_model.plan
                        book_model_plan += ' ' + str(pk) + ' '
                        book_model.plan = book_model_plan
                        book_model.save()
                    except:
                        pass
                else:
                    booked_people = item.booked_people
                    booked_people += ' ' + 'anonumous' + ' ' #anonumousは電話予約された場合の人
                booked_people_name = item.booked_people_name
                booked_people_name += ' ' + add_booked_people + ' '
                #記録
                item.number_of_people = len(booked_people.split())
                item.booked_people = booked_people
                item.booked_people_name = booked_people_name
                item.save()
            else:
                context = {
                    'month_num': month,
                    'item': item,
                    'booked_people_name_list': enumerate(booked_people_name_list),
                    'people_num': len(booked_people_name_list),
                    'first_time': item.time[:item.time.index(':')], #始めの時間
                    'first_half_time': item.time[item.time.index(':') + 1: item.time.index('-')],
                    'last_time': item.time[item.time.index('-') + 1: item.time.index(':', 5)], #終わりの時間
                    'last_half_time': item.time[item.time.index(':', 5) + 1:],
                    'setting_plan_model': setting_plan_model,
                    'error': '入力された追加の予約者は既に予約されています．',
                }
                return render(request, 'plan_update.html', context)
        item.time = time
        item.location = location
        item.max_book = max_book
        item.save()
        return redirect('detail', month, item.date)
    context = {
        'month_num': month,
        'item': item,
        'booked_people_name_list': enumerate(booked_people_name_list),
        'people_num': len(booked_people_name_list),
        'first_time': item.time[:item.time.index(':')], #始めの時間
        'first_half_time': item.time[item.time.index(':') + 1: item.time.index('-')],
        'last_time': item.time[item.time.index('-') + 1: item.time.index(':', 5)], #終わりの時間
        'last_half_time': item.time[item.time.index(':', 5) + 1:],
        'setting_plan_model': setting_plan_model,
        'error': "",
    }
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
    
    
#プラン一覧
class SettingPlanList(ListView):
    template_name = 'setting_plan_detail.html'
    model = SettingPlanModel

    def get_queryset(self):
        return super().get_queryset().order_by('plan_num')

#プラン設定の編集
class SettingPlanUpdate(UpdateView):
    template_name = 'setting_plan_update.html'
    model = SettingPlanModel
    fields = ('short_plan_name', 'price', 'location', 'max_book', 'memo', 'image')
    success_url = reverse_lazy('setting_plan')


#新しいプランの生成
from ..forms import CreateSettingPlanForm
class YogaCreate(CreateView):
    template_name = 'create.html'
    model = SettingPlanModel
    form_class = CreateSettingPlanForm
    success_url = reverse_lazy('yoga_create_plan_num')

@login_required
def yoga_create_plan_num(request):
    item = SettingPlanModel.objects.get(plan_num=0)
    setting_plan_model = SettingPlanModel.objects.all()
    plan_num_max = max([item.plan_num for item in setting_plan_model])
    item.plan_num = plan_num_max + 1
    item.save()
    return redirect('setting_plan')

                            
#プランの削除
class YogaPlanDelete(DeleteView):
    template_name = 'yoga_plan_delete.html'
    model = SettingPlanModel
    success_url = reverse_lazy('setting_plan')


#お知らせ機能
@login_required
def notefunc(request):
    item = NoteModel.objects.get(num=0)
    if request.method == "POST":
        memo = request.POST['memo']
        monday = request.POST['monday']
        if monday != "10":
            item.monday = int(monday)
        item.memo = memo
        item.save()
    context = {
        'item': item
    }
    return render(request, 'note.html', context)


################カレンダーの曜日別デフォルト日程設定######################
#設定
@login_required
def calendar_dafault_func(request):
    weekday_default_model = WeekdayDefaultModel.objects.all().order_by('time')
    monday_plan_list = list(weekday_default_model.filter(weekday='monday'))
    tuesday_plan_list = list(weekday_default_model.filter(weekday='tuesday'))
    wednesday_plan_list = list(weekday_default_model.filter(weekday='wednesday'))
    thursday_plan_list = list(weekday_default_model.filter(weekday='thursday'))
    friday_plan_list = list(weekday_default_model.filter(weekday='friday'))
    saturday_plan_list = list(weekday_default_model.filter(weekday='saturday'))
    plan_list = [monday_plan_list, tuesday_plan_list, wednesday_plan_list, thursday_plan_list, friday_plan_list, saturday_plan_list]
    #月曜日が非表示の時
    monday = NoteModel.objects.get(num=0).monday
    weekday_get_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    if  monday == 0:
        plan_list.pop(0)
        weekday_get_list.pop(0)
    #並び替え
    new_plan_list = []
    for item_list in plan_list:
        if len(item_list) >= 2:
            try:
                plan = sorted(item_list, key = lambda x: x.time)
            except:
                pass
            new_plan_list.append(plan)
        else:
            new_plan_list.append(item_list)
    plan_list = new_plan_list.copy()
    total_checkbox = len(plan_list)
    plan_list = zip(weekday_get_list ,plan_list)
    #予定入力設定
    setting_plan_model = SettingPlanModel.objects.all().order_by('plan_num')
    if request.method == "POST":
        #formの値の取得
        weekday_str = request.POST["select_days"]
        select_plan = request.POST["select_plan"]
        plan = list(setting_plan_model)[int(select_plan)].name
        time1 = request.POST["time1"]
        time1_5 = request.POST["time1-5"]
        time2 = request.POST["time2"]
        time2_5 = request.POST["time2-5"]
        location = request.POST["select_plan2"]
        max_book = request.POST["max_book"]
        #整理
        weekday_list = weekday_str.split()
        time = time1 + ":" + time1_5 + "-" + time2 + ":" + time2_5
        plan_num = SettingPlanModel.objects.get(name=plan).plan_num
        #新規作成
        for weekday in weekday_list:
            create_plan = WeekdayDefaultModel.objects.create()
            create_plan.weekday = weekday
            create_plan.plan = plan
            create_plan.time = time
            create_plan.plan_num = plan_num
            create_plan.location = location
            create_plan.max_book = max_book
            create_plan.save()
        return redirect('calendar_default')

    context = {
        'plan_list': plan_list,
        'monday': monday,
        'total_checkbox': total_checkbox,
        'setting_plan_model': enumerate(setting_plan_model),
        'setting_plan_model2': setting_plan_model
    }
    return render(request, 'weekday_default.html', context)
    
    
#各曜日の詳細確認
@login_required
def weekday_detail_func(request, weekday):
    weekday_dict = {'monday': '月曜日', 'tuesday': '火曜日', 'wednesday': '水曜日', 'thursday': '木曜日', 'friday': '金曜日', 'saturday': '土曜日'}
    weekday_default_model = list(WeekdayDefaultModel.objects.filter(weekday=weekday).order_by('time'))
    setting_plan_model = list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in weekday_default_model)
    username = request.user.get_username()
    object_plan_list = zip(weekday_default_model, setting_plan_model)
    context = {
        'weekday': weekday,
        'weekday_j': weekday_dict[weekday],
        'object_plan_list': object_plan_list,
    }
    return render(request, 'weekday_detail.html', context)
 
 
#曜日別プランの編集
@login_required
def weekday_update_func(request, weekday, pk):
    weekday_dict = {'monday': '月曜日', 'tuesday': '火曜日', 'wednesday': '水曜日', 'thursday': '木曜日', 'friday': '金曜日', 'saturday': '土曜日'}
    item = WeekdayDefaultModel.objects.get(pk=pk)
    setting_plan_model = SettingPlanModel.objects.all()
    #表示処理
    if request.method == "POST": #入力された時の処理
        time1 = request.POST["time1"]
        time1_5 = request.POST["time1-5"]
        time2 = request.POST["time2"]
        time2_5 = request.POST["time2-5"]
        time = time1 + ":" + time1_5 + "-" + time2 + ":" + time2_5
        location = request.POST['location']
        max_book = request.POST['max_book']
        item.time = time
        item.location = location
        item.max_book = max_book
        item.save()
        return redirect('weekday_detail', item.weekday)
    context = {
        'weekday_j': weekday_dict[weekday],
        'item': item,
        'first_time': item.time[:item.time.index(':')], #始めの時間
        'first_half_time': item.time[item.time.index(':') + 1: item.time.index('-')],
        'last_time': item.time[item.time.index('-') + 1: item.time.index(':', 5)], #終わりの時間
        'last_half_time': item.time[item.time.index(':', 5) + 1:],
        'setting_plan_model': setting_plan_model,
    }
    return render(request, 'weekday_update.html', context)


#曜日別プランの削除
class WeekdayPlanDelete(DeleteView):
    template_name = 'weekday_delete.html'
    model = WeekdayDefaultModel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        weekday_dict = {'monday': '月曜日', 'tuesday': '火曜日', 'wednesday': '水曜日', 'thursday': '木曜日', 'friday': '金曜日', 'saturday': '土曜日'}
        context['weekday_j'] = weekday_dict[self.kwargs['weekday']]
        return context
    
    def get_success_url(self):
        return reverse('weekday_detail', kwargs={'weekday': self.object.weekday})