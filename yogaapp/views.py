from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
import pytz
import calendar
from .models import PlanModel, SettingPlanModel, BookModel, NoteModel
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, ListView
from django.urls import reverse_lazy, reverse

def signupfunc(request):
    if request.method == "POST":
        username = request.POST['username']
        password = 'password'
        last_name = request.POST['lastname']
        first_name = request.POST['firstname']
        email = request.POST['email']
        try:
            user = User.objects.create_user(username, '', password)
            user.is_active = True
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            user_plan = BookModel.objects.create()
            user_plan.user = username
            user_plan.save()
            return redirect('login')
        except:
            return render(request, 'signup.html', {'error': 'このユーザーは登録されています'})
    return render(request, 'signup.html')


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
            
    item = NoteModel.objects.get(num=0)
    context = {
        'memo': item.memo
    }
    return render(request, 'login.html', context)


def logoutfunc(request):
    logout(request)
    return redirect('login')    


@login_required
def bookfunc(request, month):
    #カレンダーの作製
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    month2 = int(int(month) / 100 + now.month)
    next_month = month2 + 1
    pre_month = month2 - 1
    year = now.year
    if month2 > 12: #12月から1月へのバグ回避
        year += 1
        month2 -= 12
    if next_month > 12:
        next_month -= 12 * abs(int(next_month/12))
        print(next_month)
    if next_month <= 0:
        next_month += 12 * (abs(int(next_month/12)) + 1)
    if pre_month > 12:
        pre_month -= 12 * abs(int(pre_month/12))
    if pre_month <= 0:
        pre_month += 12 * (abs(int(pre_month/12)) + 1)
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
    month3 = '0' + str(month2) if len(str(month2)) == 1 else str(month2) #1ケタの月の先頭に0を足す
    object_list = list(PlanModel.objects.filter(month=str(year) + "-" + month3))
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
        zip(c_list[22:27], object_list[22:27], plan_list[22:27]),
        zip(c_list[29:34], object_list[29:34], plan_list[29:34]),
        zip(c_list[36:41], object_list[36:41], plan_list[36:41])
        ]
    if c_list[1:6].count(' ') == 5: #1行少ない時用
        calendar_list_all.pop(0)
    if c_list[36:41].count(' ') == 5 or c_list[36:41] == []: #1行少ない時用
        calendar_list_all.pop(-1)
    if c_list[29:34].count(' ') == 5 or c_list[29:34] == []: #1行少ない時用
        calendar_list_all.pop(-1)
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
        'pre_month': pre_month,
        'next_month': next_month,
        'calendar_list_all': calendar_list_all,
        'location': 'callendar'
    }
    return render(request, 'book.html', context)


#予約確定画面
@login_required
def confirmfunc(request, date):
    weekday_d = {0:'月', 1:'火', 2:'水', 3:'木', 4:'金', 5:'土', 6:'日'}
    weekday = weekday_d[datetime.datetime.strptime(date, '%Y-%m-%d').weekday()]
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
     #並び替え処理       
    time_list = [item.time for item in object_list]
    try: #同じ時間がある時バグが生じる
        object_plan_error_list = sorted(zip(time_list, object_list, plan_model_list, error_booked))
    except:
        object_plan_error_list = zip(time_list, object_list, plan_model_list, error_booked)
    context = {
        'month': date[5:7],
        'day': date[8:],
        'object_plan_error_list': object_plan_error_list,
        'weekday': weekday
    }
    return render(request, 'confirm.html', context)


#planの予約者数
def get_yoga_func(request, date, pk):
    objects = PlanModel.objects.get(pk=pk)
    item = SettingPlanModel.objects.get(plan_num=objects.plan_num)
    username = request.user.get_username()
    name = User.objects.get(username=username).last_name + User.objects.get(username=username).first_name
    if username in objects.booked_people.split(): #予約者の重複を無くすための処理
        return redirect('book', '0')
    else:
        objects.booked_people += username + ' ' 
        objects.booked_people_name += name + ' '
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
    name = User.objects.get(username=username).last_name + User.objects.get(username=username).first_name
    booked_people_list = objects.booked_people.split()
    booked_people_name_list = objects.booked_people_name.split()
    #プランで予約した人の削除
    booked_people_list.remove(username)
    booked_people_name_list.remove(name)
    objects.number_of_people = len(booked_people_list) #予約人数を減らす
    booked_people_str = ''
    booked_people_name_str = ''
    for booked_people in booked_people_list:
        booked_people_str += booked_people + ' '
    for booked_people_name in booked_people_name_list:
        booked_people_name_str += booked_people_name + ' '
    objects.booked_people = booked_people_str
    objects.booked_people_name = booked_people_name_str
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
    clean_plan(username)
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
    object_list = sorted(object_list, key = lambda x: (x.date, x.time))
    #予約したプランのプラン設定の取得
    weekday_d = {0:'月', 1:'火', 2:'水', 3:'木', 4:'金', 5:'土', 6:'日'}
    weekday_list = []
    for item in object_list:
        weekday_list.append(weekday_d[item.date.weekday()])
    plan_model_list = list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in object_list)
    context = {
        'object_list': zip(object_list, plan_model_list, weekday_list),
        'check': 0 if object_list == [] else 1,
        'location': 'booked_list'
    }
    return render(request, 'booked_list.html', context)

#ユーザー別のプランpkの掃除
def clean_plan(username):
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month, today.day)
    book_model = BookModel.objects.get(user=username)
    pk_list = book_model.plan.split()
    new_pk_list = []
    for i in range(len(pk_list)):
        PK = int(pk_list[i])
        try:
            DATE = PlanModel.objects.get(pk=PK).date
            booked_people = PlanModel.objects.get(pk=PK).booked_people.split() #プランモデルの方に名前が入っているかの確認
            if (datetime.datetime(DATE.year, DATE.month, DATE.day) - today).days >= 0 and username in booked_people:
                new_pk_list.append(str(PK))
        except: #指定pkプランが削除されていた場合のバグ回避
            pass
    #記録
    pk_str = ''
    for p in new_pk_list:
        pk_str += p + ' '
    book_model.plan = pk_str
    book_model.save()
    

#アクセス
@login_required
def access_func(request):
    return render(request, 'access.html', {'location': 'access'})

#インフォメーション
@login_required
def info_func(request):
    return render(request, 'info.html', {'location': 'info'})


############################################################
#管理者用
@login_required
def book_adminfunc(request, month):
    #カレンダーの作製
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    month2 = int(int(month) / 100 + now.month)
    next_month = month2 + 1
    pre_month = month2 - 1
    year = now.year
    if month2 > 12: #12月から1月へのバグ回避
        year += 1 * abs(int(month2/12))
        month2 -= 12 * abs(int(month2/12))
    if month2 <= 0:
        year -= 1 * (abs(int(month2/12)) + 1)
        month2 += 12 * (abs(int(month2/12)) + 1)
    if next_month > 12:
        next_month -= 12 * abs(int(next_month/12))
    if next_month <= 0:
        next_month += 12 * (abs(int(next_month/12)) + 1)
    if pre_month > 12:
        pre_month -= 12 * abs(int(pre_month/12))
    if pre_month <= 0:
        pre_month += 12 * (abs(int(pre_month/12)) + 1)
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
    month3 = '0' + str(month2) if len(str(month2)) == 1 else str(month2) #1ケタの月の先頭に0を足す
    object_list = list(PlanModel.objects.filter(month=str(year) + "-" + month3))
    c_list_plan = [] #オブジェクトリスト
    plan_list = []
    time_list = []
    for c in c_list:
        true_or_false = True
        for item in object_list:
            if str(item.date.day) == c and true_or_false == True:
                c_list_plan.append(item)
                plan_list.append([item])
                time_list.append([item.time])
                true_or_false = False
            elif str(item.date.day) == c and true_or_false == False: #同じ日付がある時
                a = plan_list[-1]
                a.append(item)
                b = time_list[-1]
                b.append(item.time)
                plan_list.pop(-1)
                plan_list.append(a)
                time_list.pop(-1)
                time_list.append(b)
        if true_or_false:
            c_list_plan.append('')
            plan_list.append('')
            time_list.append('')
    #並び替えの処理
    new_plan_list = []
    for time, plan in zip(time_list, plan_list):
        if len(time) >= 2:
            try:
                plan = [item for _, item in sorted(zip(time, plan))]
            except:
                pass
            new_plan_list.append(plan)
        else:
            new_plan_list.append(plan)
    plan_list = new_plan_list.copy()
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
        zip(c_list[22:27], object_list[22:27], plan_list[22:27]),
        zip(c_list[29:34], object_list[29:34], plan_list[29:34]),
        zip(c_list[36:41], object_list[36:41], plan_list[36:41])
        ]
    if c_list[1:6].count(' ') == 5: #1行少ない時用
        calendar_list_all.pop(0)
    if c_list[36:41].count(' ') == 5 or c_list[36:41] == []: #1行少ない時用
        calendar_list_all.pop(-1)
    if c_list[29:34].count(' ') == 5 or c_list[29:34] == []: #1行少ない時用
        calendar_list_all.pop(-1)
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
    setting_plan_model = sorted(setting_plan_model, key = lambda x: x.plan_num)
    if request.method == "POST":
        #formの値の取得
        days = request.POST["select_days"]
        select_plan = request.POST["select_plan"]
        plan = list(setting_plan_model)[int(select_plan)].name
        time1 = request.POST["time1"]
        time1_5 = request.POST["time1-5"]
        time2 = request.POST["time2"]
        time2_5 = request.POST["time2-5"]
        location = request.POST["select_plan2"]
        max_book = request.POST["max_book"]
        #整理
        month3 = '0' + str(month2) if len(str(month2)) == 1 else str(month2) #1ケタの月の先頭に0を足す
        year_month = str(year) + "-" + month3
        days_list = days.split()
        time = time1 + ":" + time1_5 + "-" + time2 + ":" + time2_5
        plan_num = SettingPlanModel.objects.get(name=plan).plan_num
        #新規作成
        for day in days_list:
            create_plan = PlanModel.objects.create()
            create_plan.date = year_month + "-" + day
            create_plan.month = year_month
            create_plan.plan = plan
            create_plan.time = time
            create_plan.plan_num = plan_num
            create_plan.location = location
            create_plan.max_book = max_book
            create_plan.save()
        return redirect('book_admin', month)
    
    context = {
        'month': month,
        'month2': month2,
        'year': year,
        'calendar_list_all': calendar_list_all,
        'total_checkbox': total_checkbox,
        'setting_plan_model': enumerate(setting_plan_model),
        'setting_plan_model2': setting_plan_model,
        'next_month': next_month,
        'pre_month': pre_month,
    }
    return render(request, 'book_admin.html', context)


#詳細確認
@login_required
def detail_admin_func(request, date):
    object_list = list(PlanModel.objects.filter(date=date))
    plan_model_list = list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in object_list)
    username = request.user.get_username()
    #予約者の抽出
    booked_people_name_list = []
    for item in object_list:
        booked_people_name_str = item.booked_people_name
        booked_people_name_str2 = ""
        for booked_people_name in booked_people_name_str.split():
            booked_people_name_str2 += '　' + booked_people_name + ','
        booked_people_name_str2 = booked_people_name_str2[1:-1] #無駄な文字の削除
        booked_people_name_list.append(booked_people_name_str2)
    #並び替えの処理
    time_list = [item.time for item in object_list]
    try:
        object_plan_name_list = sorted(zip(time_list, object_list, plan_model_list, booked_people_name_list))
        error = ''
    except:
        object_plan_name_list = zip(time_list, object_list, plan_model_list, booked_people_name_list)
        error = '時間が重複しています．'
    context = {
        'date': date,
        'object_plan_name_list': object_plan_name_list,
        'error': error,
    }
    return render(request, 'detail_admin.html', context)
 
 
#プランの編集
@login_required
def plan_update(request, date, pk):
    item = PlanModel.objects.get(pk=pk)
    setting_plan_model = SettingPlanModel.objects.all()
    #表示処理
    booked_people_name_list = item.booked_people_name.split()
    if request.method == "POST": #入力された時の処理
        add_booked_people = request.POST['add_booked_people'].replace('　', '').replace(' ', '') #空白削除
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
        if add_booked_people != '': #予約追加の人がいるとき
            if add_booked_people not in item.booked_people_name.split():
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
        return redirect('detail', item.date)
    context = {
        'item': item,
        'booked_people_name_list': enumerate(booked_people_name_list),
        'people_num': len(booked_people_name_list),
        'first_time': item.time[:item.time.index(':')], #始めの時間
        'first_half_time': item.time[item.time.index(':') + 1: item.time.index('-')],
        'last_time': item.time[item.time.index('-') + 1: item.time.index(':', 5)], #終わりの時間
        'last_half_time': item.time[item.time.index(':', 5) + 1:],
        'setting_plan_model': setting_plan_model,
    }
    return render(request, 'plan_update.html', context)


#カレンダーの予約の削除
class PlanDelete(DeleteView):
    template_name = 'plan_delete.html'
    model = PlanModel
    success_url = reverse_lazy('book_admin', kwargs={'month': '0'})        

    def get_context_data(self, **kwargs):
        print(self.kwargs)
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
    fields = ('name', 'price', 'location', 'max_book', 'memo')
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
    
#登録者情報
@login_required
def users_detail(request):
    users_list = list(User.objects.all())
    context = {
        'users_list': users_list,
    }
    return render(request, 'users.html', context)

#売上やピボットテーブル
@login_required
def analysis_func(request):
    #DataFrameの取得
    from django_pandas.io import read_frame
    plan_model = PlanModel.objects.all()
    columns = [item.name for item in PlanModel._meta.get_fields()]
    df = read_frame(plan_model, fieldnames=columns)
    df = df.sort_values(['date', 'time'])
    df.reset_index(inplace=True)
    #日付の最小値と最大値の選定
    from dateutil.relativedelta import relativedelta
    min_month = df.iloc[0, :].month
    max_month = df.iloc[-1, :].month
    month_list = sorted(list(set(df.month)))
    today = datetime.datetime.today()
    one_month_ago = today - relativedelta(months=1)
    month2 = '0' + str(one_month_ago.month) if len(str(one_month_ago.month)) == 1 else str(one_month_ago.month)
    month3 = '0' + str(today.month) if len(str(today.month)) == 1 else str(today.month)
    from_month = str(today.year) + '-' + month2 #デフォルト値
    to_month = str(today.year) + '-' + month3
    error1 = ''
    
    #入力された時の処理
    if request.method == "POST": 
        from_month = request.POST['from_month']
        to_month = request.POST['to_month']

    #dfの編集
    from_month_num = list(df.query('month == "{}"'.format(from_month)).index)[0]
    to_month_num = 1 + list(df.query('month == "{}"'.format(to_month)).index)[-1]
    if from_month_num >= to_month_num:
        from_month = str(today.year) + '-' + month2
        to_month = str(today.year) + '-' + month3
        from_month_num = list(df.query('month == "{}"'.format(from_month)).index)[0]
        to_month_num = 1 + list(df.query('month == "{}"'.format(to_month)).index)[-1]
        error1 = '期間が矛盾しています．'
    df = df.iloc[from_month_num: to_month_num]
    #曜日columnの追加
    weekday_d = {0:'月', 1:'火', 2:'水', 3:'木', 4:'金', 5:'土', 6:'日'}
    format = lambda x: weekday_d[x.weekday()]
    df.loc[:, 'weekday'] = df.loc[:, 'date'].map(format)
    #予約率columnの追加
    format = lambda x: round(x['number_of_people'] / x['max_book'] * 100, 1)
    df.loc[:, 'rate_of_book'] = df.apply(format, axis=1)
    #料金columnの追加
    setting_plan_model = SettingPlanModel.objects.all()
    format = lambda x: setting_plan_model.get(name=x).price
    df.loc[:, 'price'] = df['plan'].map(format)
    #売上columnの追加
    format = lambda x: x['price'] * x['number_of_people']
    df.loc[:, 'total_price'] = df.apply(format, axis=1)
    #月ごとの売上金額の集計
    total_price_per_month = df.groupby('month')[['number_of_people', 'total_price']].sum()
    #曜日とプランのpivot_table
    weekday_plan_rate_pivot = df.pivot_table('rate_of_book', index='weekday', columns='plan', aggfunc='mean', fill_value=0, margins=True)
    weekday_plan_rate_pivot = weekday_plan_rate_pivot.reindex(index=['火', '水', '木', '金', '土', 'All']).fillna(0)
    weekday_plan_rate_pivot = weekday_plan_rate_pivot.round(1)
    weekday_plan_totalprice_pivot = df.pivot_table('total_price', index='weekday', columns='plan', aggfunc='sum', fill_value=0, margins=True)
    weekday_plan_totalprice_pivot = weekday_plan_totalprice_pivot.reindex(index=['火', '水', '木', '金', '土', 'All']).fillna(0)
    weekday_plan_totalprice_pivot.astype('int')
    plan_name_list = list(weekday_plan_rate_pivot.columns)
    #時間のpivot_table
    time_plan_rate_pivot = df.pivot_table('rate_of_book', index='time', columns='plan', aggfunc='mean', margins=True)
    time_weekday_rate_pivot = df.pivot_table('rate_of_book', index='time', columns='weekday', aggfunc='mean', margins=True)
    print(time_plan_rate_pivot)
    print(time_weekday_rate_pivot)
    #予約者の頻度ランキング
    import collections
    booked_people_list = [x.split() for x in df.booked_people_name if x != '']
    booked_people_list2 = []
    for booked_people in booked_people_list:
        booked_people_list2 += booked_people
    booked_people_count = dict(collections.Counter(booked_people_list2))
    booked_people_count = sorted(booked_people_count.items(), key=lambda x:x[1], reverse=True)
    keys = []
    values = []
    for key, value in booked_people_count:
        keys.append(key)
        values.append(value)
    rank = [i + 1 for i in range(len(keys))]
    
    context = {
        'error1': error1,
        'from_month': from_month,
        'to_month': to_month,
        'month_list': month_list,
        'total_price_per_month': total_price_per_month,
        'weekday_plan_rate_pivot': weekday_plan_rate_pivot,
        'weekday_plan_totalprice_pivot': weekday_plan_totalprice_pivot,
        'plan_name_list': plan_name_list,
        'booked_people_count': zip(rank, keys, values),
    }
    return render(request, 'analysis.html', context)
    
#テーブル
@login_required
def table_func(request):
    #DataFrameの取得
    from django_pandas.io import read_frame
    plan_model = PlanModel.objects.all()
    columns = [item.name for item in PlanModel._meta.get_fields()]
    df = read_frame(plan_model, fieldnames=columns)
    df = df.sort_values(['date', 'time'])
    df.reset_index(inplace=True)
    #日付の最小値と最大値の選定
    from dateutil.relativedelta import relativedelta
    min_month = df.iloc[0, :].month
    max_month = df.iloc[-1, :].month
    month_list = sorted(list(set(df.month)))
    today = datetime.datetime.today()
    one_month_ago = today - relativedelta(months=1)
    month2 = '0' + str(one_month_ago.month) if len(str(one_month_ago.month)) == 1 else str(one_month_ago.month)
    month3 = '0' + str(today.month) if len(str(today.month)) == 1 else str(today.month)
    from_month =  str(today.year) + '-' + month2
    to_month = str(today.year) + '-' + month3
    error1 = ''
    
    #入力された時の処理
    if request.method == "POST": 
        from_month = request.POST['from_month']
        to_month = request.POST['to_month']

    #dfの編集
    from_month_num = list(df.query('month == "{}"'.format(from_month)).index)[0]
    to_month_num = 1 + list(df.query('month == "{}"'.format(to_month)).index)[-1]
    if from_month_num >= to_month_num:
        from_month =  str(today.year) + '-' + month2
        to_month = str(today.year) + '-' + month3
        from_month_num = list(df.query('month == "{}"'.format(from_month)).index)[0]
        to_month_num = 1 + list(df.query('month == "{}"'.format(to_month)).index)[-1]
        error1 = '期間が矛盾しています．'
    df = df.iloc[from_month_num: to_month_num]
    #曜日columnの追加
    weekday_d = {0:'月', 1:'火', 2:'水', 3:'木', 4:'金', 5:'土', 6:'日'}
    format = lambda x: weekday_d[x.weekday()]
    df['weekday'] = df['date'].map(format)
    #予約率columnの追加
    format = lambda x: round(x['number_of_people'] / x['max_book'] * 100, 1)
    df['rate_of_book'] = df.apply(format, axis=1)
    #料金columnの追加
    setting_plan_model = SettingPlanModel.objects.all()
    format = lambda x: setting_plan_model.get(name=x).price
    df['price'] = df['plan'].map(format)
    #売上columnの追加
    format = lambda x: x['price'] * x['number_of_people']
    df['total_price'] = df.apply(format, axis=1)
    context = {
        'error1': error1,
        'df': df,
        'from_month': from_month,
        'to_month': to_month,
        'month_list': month_list,
    }
    return render(request, 'table.html', context)
    


#管理者用サインアップページ
@login_required
def signup_admin_func(request):
    if request.method == "POST":
        username = request.POST['username']
        password = 'password'
        last_name = request.POST['lastname']
        first_name = request.POST['firstname']
        email = request.POST['email']
        try:
            user = User.objects.create_user(username, '', password)
            user.is_active = True
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            user_plan = BookModel.objects.create()
            user_plan.user = username
            user_plan.save()
            return redirect('signup_admin')
        except:
            return render(request, 'signup.html', {'error': 'このユーザーは登録されています'})
    return render(request, 'signup_admin.html')

#お知らせ機能
@login_required
def notefunc(request):
    item = NoteModel.objects.get(num=0)
    if request.method == "POST":
        memo = request.POST['memo']
        item.memo = memo
        item.save()
    context = {
        'item': item
    }
    return render(request, 'note.html', context)