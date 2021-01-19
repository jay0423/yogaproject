from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
import pytz
import calendar
from .models import PlanModel, SettingPlanModel, BookModel, NoteModel, WeekdayDefaultModel
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
    
    plan_list_short = []
    short_dict = {'ヨガ': 'ヨガ', '椅子ヨガ': '椅子', 'お茶会': 'お茶', '蔵のカフェ': '蔵', 'キッズヨガ': 'キッズ'}
    for plan in plan_list:
        if plan != '':
            p_list = []
            for p in plan:
                try:
                    p_list.append(short_dict[p])
                except:
                    p_list.append(p)
            plan_list_short.append(p_list)
        else:
            plan_list_short.append(plan)
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
################月曜日と日曜日を非表示にする場合################
    monday = NoteModel.objects.get(num=0).monday
    if monday == 0:
        calendar_list_all = [
            zip(c_list[1:6], object_list[1:6], plan_list[1:6], plan_list_short[1:6]),
            zip(c_list[8:13], object_list[8:13], plan_list[8:13], plan_list_short[8:13]),
            zip(c_list[15:20], object_list[15:20], plan_list[15:20], plan_list_short[15:20]),
            zip(c_list[22:27], object_list[22:27], plan_list[22:27], plan_list_short[22:27]),
            zip(c_list[29:34], object_list[29:34], plan_list[29:34], plan_list_short[29:34]),
            zip(c_list[36:41], object_list[36:41], plan_list[36:41], plan_list_short[36:41])
            ]
        if c_list[1:6].count(' ') == 5: #1行少ない時用
            calendar_list_all.pop(0)
        if c_list[36:41].count(' ') == 5 or c_list[36:41] == []: #1行少ない時用
            calendar_list_all.pop(-1)
        if c_list[29:34].count(' ') == 5 or c_list[29:34] == []: #1行少ない時用
            calendar_list_all.pop(-1)
    ################月曜日を非表示にしない場合################
    elif monday == 1:
        calendar_list_all = [
            zip(c_list[0:6], object_list[0:6], plan_list[0:6], plan_list_short[0:6]),
            zip(c_list[7:13], object_list[7:13], plan_list[7:13], plan_list_short[7:13]),
            zip(c_list[14:20], object_list[14:20], plan_list[14:20], plan_list_short[14:20]),
            zip(c_list[21:27], object_list[21:27], plan_list[21:27], plan_list_short[21:27]),
            zip(c_list[28:34], object_list[28:34], plan_list[28:34], plan_list_short[28:34]),
            zip(c_list[35:41], object_list[35:41], plan_list[35:41], plan_list_short[35:41])
            ]
        if c_list[0:6].count(' ') == 6: #1行少ない時用
            calendar_list_all.pop(0)
        if c_list[35:41].count(' ') == 6 or c_list[35:41] == []: #1行少ない時用
            calendar_list_all.pop(-1)
        if c_list[28:34].count(' ') == 6 or c_list[28:34] == []: #1行少ない時用
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
        'location': 'callendar',
        'monday': monday,
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
    #デフォルト入力の必要性を確認
    if len(object_list) == 0:
        default_needs = True
    else:
        default_needs = False
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
    monday = NoteModel.objects.get(num=0).monday
    total_checkbox = 0
    if monday == 0:
        new_c_list = c_list[1:6] + c_list[8:13] + c_list[15:20] + c_list[22:27] + c_list[29:34] + c_list[36:41]
    elif monday == 1:
        new_c_list = c_list[0:6] + c_list[7:13] + c_list[14:20] + c_list[21:27] + c_list[28:34] + c_list[35:41]
    for c in new_c_list:
        if c != ' ':
            total_checkbox += 1
    ################月曜日と日曜日を非表示にする場合################
    if monday == 0:
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
    ################月曜日を非表示にしない場合################
    elif monday == 1:
        calendar_list_all = [
            zip(c_list[0:6], object_list[0:6], plan_list[0:6]),
            zip(c_list[7:13], object_list[7:13], plan_list[7:13]),
            zip(c_list[14:20], object_list[14:20], plan_list[14:20]),
            zip(c_list[21:27], object_list[21:27], plan_list[21:27]),
            zip(c_list[28:34], object_list[28:34], plan_list[28:34]),
            zip(c_list[35:41], object_list[35:41], plan_list[35:41])
            ]
        if c_list[0:6].count(' ') == 6: #1行少ない時用
            calendar_list_all.pop(0)
        if c_list[35:41].count(' ') == 6 or c_list[35:41] == []: #1行少ない時用
            calendar_list_all.pop(-1)
        if c_list[28:34].count(' ') == 6 or c_list[28:34] == []: #1行少ない時用
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
        default = int(request.POST["default_or_not"])
        if default == 0:
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
            add_plans = []
            for day in days_list:
                plans = PlanModel(date=year_month + "-" + day, month=year_month, plan=plan, time=time, plan_num=plan_num, location=location, max_book=max_book)
                add_plans.append(plans)
            PlanModel.objects.bulk_create(add_plans)
            return redirect('book_admin', month)

        elif default == 1: #デフォルト入力時
            weekday_default_model = WeekdayDefaultModel.objects.all()
            month3 = '0' + str(month2) if len(str(month2)) == 1 else str(month2) #1ケタの月の先頭に0を足す
            year_month = str(year) + "-" + month3
            #日にちと曜日のリストの作成
            for i in range(new_c_list.count(' ')):
                new_c_list.remove(' ')
            weekday_d = {0:'monday', 1:'tuesday', 2:'wednesday', 3:'thursday', 4:'friday', 5:'saturday', 6:'sunday'}
            weekday_list = [weekday_d[datetime.datetime(int(year), int(month3), int(day)).weekday()] for day in new_c_list]
            #データの保存
            add_plans = []
            for c, weekday3 in zip(new_c_list, weekday_list):
                for item in list(weekday_default_model.filter(weekday=weekday3)):
                    #データの収集
                    plan = item.plan
                    time = item.time
                    plan_num = item.plan_num
                    location = item.location
                    max_book = item.max_book
                    #保存タプルの作成
                    plans = PlanModel(date=year_month + "-" + c, month=year_month, plan=plan, time=time, plan_num=plan_num, location=location, max_book=max_book)
                    add_plans.append(plans)
            PlanModel.objects.bulk_create(add_plans)
                
            return redirect('book_admin', month)

    context = {
        'default_needs': default_needs,
        'month': month,
        'month2': month2,
        'year': year,
        'calendar_list_all': calendar_list_all,
        'total_checkbox': total_checkbox,
        'setting_plan_model': enumerate(setting_plan_model),
        'setting_plan_model2': setting_plan_model,
        'next_month': next_month,
        'pre_month': pre_month,
        'monday': monday,
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
        context['plan'] = SettingPlanModel.objects.get(plan_num=item.plan_num)
        return context
    
    def get_success_url(self):
        return reverse('detail', kwargs={'date': self.object.date})
    
    
#プラン一覧
class SettingPlanList(ListView):
    template_name = 'setting_plan_detail.html'
    model = SettingPlanModel


#プラン設定の編集
class SettingPlanUpdate(UpdateView):
    template_name = 'setting_plan_update.html'
    model = SettingPlanModel
    fields = ('price', 'location', 'max_book', 'memo', 'image')
    success_url = reverse_lazy('setting_plan')


#新しいプランの生成
from .forms import CreateSettingPlanForm
class YogaCreate(CreateView):
    template_name = 'create.html'
    model = SettingPlanModel
    form_class = CreateSettingPlanForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            setting_plan_model = SettingPlanModel.objects.all()
            plan_num_max = max([item.plan_num for item in setting_plan_model])
            obj = form.save(commit=False)
            obj.plan_num = plan_num_max + 1
            obj.save()
            return redirect('setting_plan')
    
                            
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
    if list(plan_model) == []:
        context = {
            'post': False,
            'error1': 'データがありません．',
            'month_list': [],
            'from_month': '',
            'to_month': '',
        }
        return render(request, 'analysis.html', context)
    columns = [item.name for item in PlanModel._meta.get_fields()]
    df = read_frame(plan_model, fieldnames=columns)
    df = df.sort_values(['date', 'time'])
    df.reset_index(inplace=True)
    df = df.drop('index', axis=1)
    #日付の最小値と最大値の選定
    min_month = df.iloc[0, :].month
    max_month = df.iloc[-1, :].month
    month_list = sorted(list(set(df.month)))
    error1 = ''
    #デフォルト値
    index = 'weekday'
    columns = 'plan'
    data = 'rate_of_book'
    aggfunc = 'mean'
    columns2 = 'plan'
    #入力された時の処理
    if request.method == "POST": 
        post = True
        from_month = request.POST['from_month']
        to_month = request.POST['to_month']
        try:
            index = request.POST['index']
            columns2 = request.POST['columns']
            data = request.POST['data']
            aggfunc = request.POST['aggfunc']
        except:
            pass
        columns = 'weekday' if columns2 == 'weekday2' else columns2
        
        #dfの編集
        from_month_num = list(df.query('month == "{}"'.format(from_month)).index)[0]
        to_month_num = 1 + list(df.query('month == "{}"'.format(to_month)).index)[-1]
        if from_month_num >= to_month_num:
            context = {
                'post': False,
                'error1': '期間が矛盾しています．',
                'month_list': month_list,
                'from_month': '',
                'to_month': '',
            }
            return render(request, 'analysis.html', context)
        df = df.iloc[from_month_num: to_month_num]
        if list(df[df.loc[:, 'booked_people_name'] != ''].loc[:, 'booked_people_name']) == []:
            context = {
                'post': False,
                'error1': '予約者が一人もいません．',
                'month_list': month_list,
                'from_month': '',
                'to_month': '',
            }
            return render(request, 'analysis.html', context)
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
        #pivot_tableの作成
        pivot_table = df.pivot_table(data, index=index, columns=columns, aggfunc=aggfunc, margins=True)
        #順番の整理用
        if index == 'weekday':
            pivot_table = pivot_table.reindex(index=['月', '火', '水', '木', '金', '土', 'All'])
        if columns == 'weekday':
            columns_list = ['月', '火', '水', '木', '金', '土', 'All']
        elif columns == 'plan':
            columns_list = list(pivot_table.columns)[:-1]
            columns_num_list = []
            for plan in columns_list:
                columns_num_list.append(SettingPlanModel.objects.get(name=plan).plan_num)
            columns_list = [item for _, item in sorted(zip(columns_num_list, columns_list))] + ['All'] 
        pivot_table = pivot_table.reindex(columns=columns_list)
        #各要素を四捨五入する
        def round_func1(x):
            try:
                return round(x, 1)
            except:
                return None
        def round_func2(x):
            try:
                return str(int(x))
            except:
                return None
        if aggfunc == 'mean' or aggfunc == 'std' or aggfunc == 'median':
            if data == 'total_price':
                pivot_table = pivot_table.applymap(round_func2).dropna(axis=1, how='all').dropna(how='all').fillna('')
            else:
                pivot_table = pivot_table.applymap(round_func1).dropna(axis=1, how='all').dropna(how='all').fillna('')
        elif aggfunc == 'sum':
            pivot_table = pivot_table.applymap(round_func2).dropna(axis=1, how='all').dropna(how='all').fillna('')
        columns_list = list(pivot_table.columns)
        #表示する条件
        en_dict = {'weekday': '曜日', 'time': '時間', 'plan': 'プラン', 'rate_of_book': '予約率', 'number_of_people': '予約数', 'total_price': '売上金額', 'mean': '平均値', 'sum': '合計', 'std': '標準偏差', 'median': '中央値'}
        if data == 'rate_of_book':
            unit = '%'
        elif data == 'number_of_people':
            unit = '-'
        elif data == 'total_price':
            unit = '円'
        terms = '{}の{}【{}】｜{}－{}'.format(en_dict[data], en_dict[aggfunc], unit, en_dict[index], en_dict[columns])

        #名前を分割して行を追加する処理
        df.reset_index(inplace=True)
        df.drop('index', axis=1, inplace=True)
        df_to_csv = df.copy()
        booked_people_list = df.loc[:, 'booked_people']
        booked_people_name_list = df.loc[:, 'booked_people_name']
        index_list = list(df.index)
        for index2, booked_people, booked_people_name in zip(index_list, booked_people_list, booked_people_name_list):
            if len(booked_people.split()) > 1:
                for people, people_name in zip(booked_people.split(), booked_people_name.split()):
                    new_series = df.iloc[index2, :]
                    new_series.booked_people = people
                    new_series.booked_people_name = people_name
                    df_to_csv = df_to_csv.append(new_series)
        df_to_csv = df_to_csv[df_to_csv.loc[:, 'booked_people'].map(lambda x: len(x.split())) <= 1]
        df_to_csv = df_to_csv.sort_values(['date', 'time'])
        df_to_csv.reset_index(inplace=True)
        df_to_csv.drop('index', axis=1, inplace=True)
        df_to_csv.insert(0, 'new_id', df_to_csv.loc[:, 'date'].map(str) + df_to_csv.loc[:, 'plan'] + df_to_csv.loc[:, 'time'] + df_to_csv.loc[:, 'booked_people_name'])
        df_to_csv.loc[:, 'booked_people'] = df_to_csv.loc[:, 'booked_people'].map(lambda x: x.replace(' ', ''))
        df_to_csv.loc[:, 'booked_people_name'] = df_to_csv.loc[:, 'booked_people_name'].map(lambda x: x.replace(' ', ''))
        #予約者の頻度ランキング
        booked_people_pivot_table = df_to_csv[df_to_csv.loc[:, 'booked_people_name'] != ''].pivot_table(data, index='booked_people_name', columns='plan', aggfunc='count', fill_value=0, margins=True)
        columns_list2 = list(booked_people_pivot_table.columns)
        pivot_list = [booked_people_pivot_table[:-1].loc[:, columns].sort_values(ascending=False) for columns in columns_list2]
        rank2 = [i + 1 for i in range(len(booked_people_pivot_table[:-1].values))]
        pivot_list = [zip(rank2, list(item.index), item.values) for item in pivot_list]
        
        context = {        
            'post': post,
            'error1': error1,
            'terms': terms,
            'from_month': from_month,
            'to_month': to_month,
            'index': index,
            'columns': columns2,
            'data': data,
            'aggfunc': aggfunc,
            'month_list': month_list,
            'total_price_per_month': total_price_per_month,
            'pivot_table': pivot_table,
            'columns_list': columns_list,
            'pivot_list': zip(columns_list2, pivot_list),
            'columns_list2': columns_list2,
            'len_columns_list2': len(columns_list2),
        }
        return render(request, 'analysis.html', context)
    
    context = {
        'post': False,
        'error1': '',
        'month_list': month_list,
        'from_month': '',
        'to_month': '',
    }
    return render(request, 'analysis.html', context)
        
    
#テーブル
@login_required
def table_func(request):
    #DataFrameの取得
    from django_pandas.io import read_frame
    plan_model = PlanModel.objects.all()
    if list(plan_model) == []:
        context = {
            'post': False,
            'error1': 'データがありません．',
            'month_list': [],
            'from_month': '',
            'to_month': '',
        }
        return render(request, 'table.html', context)
    columns = [item.name for item in PlanModel._meta.get_fields()]
    df = read_frame(plan_model, fieldnames=columns)
    df = df.sort_values(['date', 'time'])
    df.reset_index(inplace=True)
    df = df.drop('index', axis=1)
    #日付の最小値と最大値の選定
    from dateutil.relativedelta import relativedelta
    min_month = df.iloc[0, :].month
    max_month = df.iloc[-1, :].month
    month_list = sorted(list(set(df.month)))
    error1 = ''
    
    #入力された時の処理
    if request.method == "POST": 
        from_month = request.POST['from_month']
        to_month = request.POST['to_month']

        #dfの編集
        from_month_num = list(df.query('month == "{}"'.format(from_month)).index)[0]
        to_month_num = 1 + list(df.query('month == "{}"'.format(to_month)).index)[-1]
        if from_month_num >= to_month_num:
            context = {
                'post': False,
                'error1': '期間が矛盾しています．',
                'month_list': month_list,
                'from_month': '',
                'to_month': '',
            }
            return render(request, 'table.html', context)
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
        df.loc[:, 'price'] = df.loc[:, 'plan'].map(format)
        #売上columnの追加
        format = lambda x: x['price'] * x['number_of_people']
        df.loc[:, 'total_price'] = df.apply(format, axis=1)
        df.reset_index(inplace=True)
        df = df.drop('index', axis=1)
        #名前を分割して行を追加する処理
        df_to_csv = df.copy()
        booked_people_list = df.loc[:, 'booked_people']
        booked_people_name_list = df.loc[:, 'booked_people_name']
        index_list = list(df.index)
        for index, booked_people, booked_people_name in zip(index_list, booked_people_list, booked_people_name_list):
            if len(booked_people.split()) > 1:
                for people, people_name in zip(booked_people.split(), booked_people_name.split()):
                    new_series = df.iloc[index, :]
                    new_series.booked_people = people
                    new_series.booked_people_name = people_name
                    df_to_csv = df_to_csv.append(new_series)
        df_to_csv = df_to_csv[df_to_csv.loc[:, 'booked_people'].map(lambda x: len(x.split())) <= 1]
        df_to_csv = df_to_csv.sort_values(['date', 'time'])
        df_to_csv.reset_index(inplace=True)
        df_to_csv.drop('index', axis=1, inplace=True)
        df_to_csv.insert(0, 'new_id', df_to_csv.loc[:, 'date'].map(str) + df_to_csv.loc[:, 'plan'] + df_to_csv.loc[:, 'time'] + df_to_csv.loc[:, 'booked_people_name'])
        df_to_csv.loc[:, 'booked_people'] = df_to_csv.loc[:, 'booked_people'].map(lambda x: x.replace(' ', ''))
        df_to_csv.loc[:, 'booked_people_name'] = df_to_csv.loc[:, 'booked_people_name'].map(lambda x: x.replace(' ', ''))
        #csvファイルで吐き出し
        df_to_csv.to_csv('static/table.csv', encoding='utf_8_sig')
        context = {
            'post': True,
            'error1': error1,
            'df': df,
            'from_month': from_month,
            'to_month': to_month,
            'month_list': month_list,
        }
        return render(request, 'table.html', context)
    context = {
        'post': False,
        'error1': '',
        'from_month': '',
        'to_month': '',
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
    weekday_default_model = WeekdayDefaultModel.objects.all()
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
    setting_plan_model = SettingPlanModel.objects.all()
    setting_plan_model = sorted(setting_plan_model, key = lambda x: x.plan_num)
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
    weekday_default_model = list(WeekdayDefaultModel.objects.filter(weekday=weekday))
    setting_plan_model = list(SettingPlanModel.objects.filter(plan_num=item.plan_num)[0] for item in weekday_default_model)
    username = request.user.get_username()
    
    #並び替えの処理
    time_list = [item.time for item in weekday_default_model]
    try:
        object_plan_list = sorted(zip(time_list, weekday_default_model, setting_plan_model))
        error = ''
    except:
        object_plan_list = zip(time_list, weekday_default_model, setting_plan_model)
        error = '時間が重複しています．'
    context = {
        'weekday': weekday,
        'weekday_j': weekday_dict[weekday],
        'object_plan_list': object_plan_list,
        'error': error,
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