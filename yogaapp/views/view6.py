"""
管理者用の設定．プラン一覧，曜日別プラン，表示設定の実装．
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import SettingPlanModel, NoteModel, WeekdayDefaultModel
from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from django.urls import reverse_lazy, reverse
from ..forms import CreateSettingPlanForm

################プラン一覧設定######################
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
    

###############表示設定，お知らせ機能，月曜日の表示設定######################
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
# from .view2 import CalendarAdmin
class WeekdayCalendar:
        
    def __init__(self):
        self.monday = NoteModel.objects.get(num=0).monday
    
    def sort_by_time(self, plan_list):
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
        return new_plan_list
        
    def make_plan_list(self):
        weekday_default_model = WeekdayDefaultModel.objects.all().order_by('time')
        monday_plan_list = list(weekday_default_model.filter(weekday='monday'))
        tuesday_plan_list = list(weekday_default_model.filter(weekday='tuesday'))
        wednesday_plan_list = list(weekday_default_model.filter(weekday='wednesday'))
        thursday_plan_list = list(weekday_default_model.filter(weekday='thursday'))
        friday_plan_list = list(weekday_default_model.filter(weekday='friday'))
        saturday_plan_list = list(weekday_default_model.filter(weekday='saturday'))
        plan_list = [monday_plan_list, tuesday_plan_list, wednesday_plan_list, thursday_plan_list, friday_plan_list, saturday_plan_list]
        #並び替え
        plan_list = self.sort_by_time(plan_list)
        return plan_list
    
    def make_weekday_list(self, plan_list):
        weekday_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        if  self.monday == 0: #月曜日が非表示の時の処理
            plan_list.pop(0)
            weekday_list.pop(0)
        return weekday_list    
    
    def get_context_data(self, setting_plan_model):
        plan_list = self.make_plan_list()
        weekday_list = self.make_weekday_list(plan_list)
        total_checkbox = len(plan_list)
        week_plan_list = zip(weekday_list ,plan_list)
        context = {
            'plan_list': week_plan_list,
            'monday': self.monday,
            'total_checkbox': total_checkbox,
            'setting_plan_model': enumerate(setting_plan_model),
            'setting_plan_model2': setting_plan_model
        }
        return context

@login_required
def calendar_dafault_func(request):
    setting_plan_model = SettingPlanModel.objects.all().order_by('plan_num')
    a = WeekdayCalendar()
    context = a.get_context_data(setting_plan_model)
    #予定入力設定
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