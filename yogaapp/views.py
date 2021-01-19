from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
import pytz
import calendar
from .models import PlanModel, SettingPlanModel, BookModel
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, ListView
from django.urls import reverse_lazy, reverse

def signupfunc(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        last_name = request.POST['lastname']
        first_name = request.POST['firstname']
        try:
            user = User.objects.create_user(username, '', password)
            user.is_active = True
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return redirect('login')
        except:
            return render(request, 'signup.html', {'error': 'このユーザーは登録されています'})
    return render(request, 'signup.html', {'some': 100})


def loginfunc(request):
    if request.method == "POST":
        username = request.POST['username']
        password = 'password'
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if User.objects.filter(username=username)[0].is_superuser:
                return redirect('book_admin', 0)
            else:
                return redirect('book', 0)
        else:
            return render(request, 'login.html', {'error': 'このユーザーは登録されていません'})
    return render(request, 'login.html')


def logoutfunc(request):
    logout(request)
    return redirect('login')    


@login_required
def bookfunc(request, month):
    #カレンダーの作製
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    month2 = int(int(month) / 100 + now.month)
    year = now.year
    if month2 > 12: #12月から1月へのバグ回避
        year += 1
        month2 -= 12
    c_str = calendar.month(year, month2)
    c_str = c_str[c_str.find('\n', 25) + 1:]
    c_list = [] #カレンダーの日付リスト
    for i, c in enumerate(c_str.split('\n')[:-1]):
        if i == 0 and len(c.split()) <= 7:
            c_list = c_list + list(' ' * (7 - len(c.split()))) + c.split()
        elif i != 0 and len(c.split()) <= 7:
            c_list = c_list + c.split() + list(' ' * (7 - len(c.split())))
        else:
            c_list += c.split()
    #プランの取得
    object_list = list(PlanModel.objects.filter(month=str(year) + "-" + str(month2)))
    c_list_plan = [] #オブジェクトリスト
    plan_list = []
    for c in c_list:
        true_or_false = True
        for item in object_list:
            if str(item.date.day) == c and true_or_false == True:
                c_list_plan.append(item)
                plan_list.append([item.plan])
                true_or_false = False
            elif str(item.date.day) == c and true_or_false == False: #同じ日付がある時
                a = plan_list[-1]
                a.append(item.plan)
                a = list(set(a)) #重複の削除
                a.sort()
                plan_list.pop(-1)
                plan_list.append(a)
        if true_or_false:
            c_list_plan.append('')
            plan_list.append('')
    # object_list = c_list_plan.copy()
    #日にちが過ぎているリストの削除
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month, today.day)
    object_list = []
    for item in c_list_plan:
        if item != '':
            date_list = str(item.date).split('-')
            if (datetime.datetime(int(date_list[0]), int(date_list[1]), int(date_list[2])) - today).days < 0:
                object_list.append('')
            else:
                object_list.append(item)
        else:
            object_list.append('')    
    calendar_list_all = [
        zip(c_list[1:6], object_list[1:6], plan_list[1:6]),
        zip(c_list[8:13], object_list[8:13], plan_list[8:13]),
        zip(c_list[15:20], object_list[15:20], plan_list[15:20]),
        zip(c_list[22:27], object_list[22:27], plan_list[22:27])
        ]
    if len(c_list) > 29: #1つ行が多い月用
        calendar_list_all.append(zip(c_list[29:34], object_list[29:34], plan_list[29:34]))
    ################月曜日と日曜日を非表示にしない場合################
    # calendar_list_all = [
    #     zip(c_list[:7], object_list[:7], plan_list[:7]),
    #     zip(c_list[7:14], object_list[7:14], plan_list[7:14]),
    #     zip(c_list[14:21], object_list[14:21], plan_list[14:21]),
    #     zip(c_list[21:28], object_list[21:28], plan_list[21:28]),
    #     zip(c_list[28:35], object_list[28:35], plan_list[28:35])
    #     ]
    # #1つ行が多い月用
    # if len(c_list) > 35:
    #     calendar_list_all.append(zip(c_list[35:], object_list[35:], plan_list[35:]))
    #############################################################
    context = {
        'month': month,
        'month2': month2,
        'calendar_list_all': calendar_list_all
    }
    return render(request, 'book.html', context)


#model内fieldの自動作成
def make_plan_auto(c_list, year, month2):
        c_list = [c for c in c_list if c != ' ']
        for c in c_list:
            new_plan = PlanModel.objects.create()
            new_plan.date = str(year) + '-' + str(month2) + '-' + str(c)
            new_plan.month = month2
            new_plan.save()


#予約確定画面
@login_required
def confirmfunc(request, date):
    object_list = list(PlanModel.objects.filter(date=date))
    plan_model_list = list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in object_list)
    username = request.user.get_username()
    #既に予約している人手はないかの確認
    error_booked = []
    for i in range(len(object_list)):
        booked_people_list = object_list[i].booked_people.split()
        if username in booked_people_list:
            error_booked.append(1) #予約済
        else:
            error_booked.append(0)
    context = {
        'date': date,
        'object_plan_error_list': zip(object_list, plan_model_list, error_booked),
    }
    return render(request, 'confirm.html', context)


#planの予約者数
def get_yoga_func(request, date, pk):
    objects = PlanModel.objects.get(pk=pk)
    username = request.user.get_username()
    if objects.number_of_people == 7:
        context = {
            'objects': objects,        
            'error': '予約人数がいっぱいです　',
        }
        return render(request, 'confirm.html', context)
    elif username in objects.booked_people.split(): #予約者の重複を無くすための処理
        return redirect('book', '0')
    else:
        objects.booked_people += username + ' ' 
        booked_people_list = objects.booked_people.split()
        objects.number_of_people = len(booked_people_list)
        objects.save()
        #ユーザー別で予約したプランを記録
        if list(BookModel.objects.filter(user=username)) == []:
            user_plan = BookModel.objects.create()
            user_plan.user = username
            user_plan.plan = str(pk)
        else:
            user_plan = BookModel.objects.filter(user=username)[0]
            try:
                user_plan.plan += ' ' + str(pk)
            except:
                user_plan.plan = str(pk)
        user_plan.save()
    return redirect('confirm', date)


#planのキャンセル
def cancel_yoga_func(request, date, pk, mark):
    objects = PlanModel.objects.get(pk=pk)
    username = request.user.get_username()
    booked_people_list = objects.booked_people.split()
    #プランで予約した人の削除
    booked_people_list.remove(username)
    objects.number_of_people = len(booked_people_list) #予約人数を減らす
    booked_people_str = ''
    for booked_people in booked_people_list:
        booked_people_str += booked_people + ' '
    objects.booked_people = booked_people_str
    objects.save()
    #ユーザー別で予約したプランの削除
    objects = BookModel.objects.filter(user=username)[0]
    plan_list = objects.plan.split()
    try:
        plan_list.remove(str(pk))
    except:
        pass
    plan_str = ''
    for plan in plan_list:
        plan_str += plan + ' '
    objects.plan = plan_str
    objects.save()
    if mark == '0':
        return redirect('confirm', date)
    elif mark == "1":
        return redirect('booked_list')


#予約したプランを返す
@login_required
def booked_list_func(request):
    username = request.user.get_username()
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month, today.day)
    if list(BookModel.objects.filter(user=username)) == []:
        user_plan = BookModel.objects.create()
        user_plan.user = username
        user_plan.save()
    if BookModel.objects.filter(user=username)[0].plan == None:
        pk_list = []
    else:
        pk_list = BookModel.objects.filter(user=username)[0].plan.split()
    #ユーザーの予約したプランのpkを取得
    object_list = []
    date_list = []
    for pk in pk_list:
        date_list_2 = str(PlanModel.objects.get(pk=pk).date).split('-')
        #日にちが今日よりも後の物のみ格納
        if (datetime.datetime(int(date_list_2[0]), int(date_list_2[1]), int(date_list_2[2])) - today).days >= 0:
            object_list.append(PlanModel.objects.get(pk=pk))
            date_list.append(PlanModel.objects.get(pk=pk).date)
    object_list = [item for _, item in sorted(zip(date_list, object_list))]
    #予約したプランのプラン設定の取得
    plan_model_list = list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in object_list)
    context = {
        'object_list': zip(object_list, plan_model_list),
        'check': 0 if object_list == [] else 1,
    }
    return render(request, 'booked_list.html', context)


############################################################
#管理者用
@login_required
def book_adminfunc(request, month):
    #カレンダーの作製
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    month2 = int(int(month) / 100 + now.month)
    year = now.year
    if month2 > 12: #12月から1月へのバグ回避
        year += 1
        month2 -= 12
    c_str = calendar.month(year, month2)
    c_str = c_str[c_str.find('\n', 25) + 1:]
    c_list = [] #カレンダーの日付リスト
    for i, c in enumerate(c_str.split('\n')[:-1]):
        if i == 0 and len(c.split()) <= 7:
            c_list = c_list + list(' ' * (7 - len(c.split()))) + c.split()
        elif i != 0 and len(c.split()) <= 7:
            c_list = c_list + c.split() + list(' ' * (7 - len(c.split())))
        else:
            c_list += c.split()
    #プランの取得
    object_list = list(PlanModel.objects.filter(month=str(year) + "-" + str(month2)))
    c_list_plan = [] #オブジェクトリスト
    plan_list = []
    for c in c_list:
        true_or_false = True
        for item in object_list:
            if str(item.date.day) == c and true_or_false == True:
                c_list_plan.append(item)
                plan_list.append([item.plan])
                true_or_false = False
            elif str(item.date.day) == c and true_or_false == False: #同じ日付がある時
                a = plan_list[-1]
                a.append(item.plan)
                # a = list(set(a)) #重複の削除
                # a.sort()
                plan_list.pop(-1)
                plan_list.append(a)
        if true_or_false:
            c_list_plan.append('')
            plan_list.append('')
    object_list = c_list_plan.copy()
    #checkboxの総数を算出する
    total_checkbox = 0
    new_c_list = c_list[1:6] + c_list[8:13] + c_list[15:20] + c_list[22:27] + c_list[29:34]
    for c in new_c_list:
        if c != ' ':
            total_checkbox += 1
    calendar_list_all = [
        zip(c_list[1:6], object_list[1:6], plan_list[1:6]),
        zip(c_list[8:13], object_list[8:13], plan_list[8:13]),
        zip(c_list[15:20], object_list[15:20], plan_list[15:20]),
        zip(c_list[22:27], object_list[22:27], plan_list[22:27])
        ]
    if len(c_list) > 29: #1つ行が多い月用
        calendar_list_all.append(zip(c_list[29:34], object_list[29:34], plan_list[29:34]))
    ################月曜日と日曜日を非表示にしない場合################
    # calendar_list_all = [
    #     zip(c_list[:7], object_list[:7], plan_list[:7]),
    #     zip(c_list[7:14], object_list[7:14], plan_list[7:14]),
    #     zip(c_list[14:21], object_list[14:21], plan_list[14:21]),
    #     zip(c_list[21:28], object_list[21:28], plan_list[21:28]),
    #     zip(c_list[28:35], object_list[28:35], plan_list[28:35])
    #     ]
    # #1つ行が多い月用
    # if len(c_list) > 35:
    #     calendar_list_all.append(zip(c_list[35:], object_list[35:], plan_list[35:]))
    #############################################################
    
    #予定入力設定
    setting_plan_model = SettingPlanModel.objects.all()
    if request.method == "POST":
        #formの値の取得
        days = request.POST["select_days"]
        plan = request.POST["select_plan"]
        time1 = request.POST["time1"]
        time2 = request.POST["time2"]
        #整理
        year_month = str(year) + "-" + str(month2)
        days_list = days.split()
        time = time1 + "～" + time2
        plan_num = setting_plan_model.filter(name=plan)[0].plan_num
        #新規作成
        for day in days_list:
            create_plan = PlanModel.objects.create()
            create_plan.date = year_month + "-" + day
            create_plan.month = year_month
            create_plan.plan = plan
            create_plan.time = time
            create_plan.plan_num = plan_num
            create_plan.save()
        return redirect('book_admin', month)
    
    context = {
        'month': month,
        'month2': month2,
        'calendar_list_all': calendar_list_all,
        'total_checkbox': total_checkbox,
        'setting_plan_model': setting_plan_model,
    }
    return render(request, 'book_admin.html', context)


#詳細確認
@login_required
def detail_admin_func(request, date):
    object_list = list(PlanModel.objects.filter(date=date))
    plan_model_list = list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in object_list)
    username = request.user.get_username()
    #予約者の抽出
    booked_people_list = []
    for item in object_list:
        booked_people_str = item.booked_people
        booked_people_str2 = ""
        for booked_people in booked_people_str.split():
            name = User.objects.get(username=booked_people).last_name + User.objects.get(username=booked_people).first_name #名前の取得
            booked_people_str2 += '　' + name + ','
        booked_people_str2 = booked_people_str2[1:-1] #無駄な文字の削除
        booked_people_list.append(booked_people_str2)
    context = {
        'date': date,
        'object_plan_name_list': zip(object_list, plan_model_list, booked_people_list),
    }
    return render(request, 'detail_admin.html', context)
 
    
#編集
class PlanUpdate(UpdateView):
    template_name = 'plan_update.html'
    model = PlanModel
    fields = ('plan', 'number_of_people', 'booked_people', 'time')

    def get_success_url(self):
        date = self.kwargs.get('date')
        return reverse('detail', kwargs={'date': self.kwargs['date']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.kwargs['date']
        return context

#カレンダーの予冷の削除
class PlanDelete(DeleteView):
    template_name = 'plan_delete.html'
    model = PlanModel
    success_url = reverse_lazy('book_admin', kwargs={'month': '0'})        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = PlanModel.objects.get(pk=self.kwargs['pk'])
        context['date'] = self.kwargs['date']
        context['plan'] = SettingPlanModel.objects.get(plan_num=item.plan_num)
        return context
    
    
#プラン一覧
class SettingPlanList(ListView):
    template_name = 'setting_plan_detail.html'
    model = SettingPlanModel


#プラン設定の編集
class SettingPlanUpdate(UpdateView):
    template_name = 'setting_plan_update.html'
    model = SettingPlanModel
    fields = ('name', 'price', 'location', 'max_book', 'memo', 'image', 'plan_num')
    success_url = reverse_lazy('setting_plan')

#新しいプランの生成
class YogaCreate(CreateView):
    template_name = 'create.html'
    model = SettingPlanModel
    fields = ('name', 'price', 'location', 'max_book', 'memo', 'image', 'plan_num')
    success_url = reverse_lazy('setting_plan')
    
#プランの削除
class YogaPlanDelete(DeleteView):
    template_name = 'yoga_plan_delete.html'
    model = SettingPlanModel
    success_url = reverse_lazy('setting_plan')
    