from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import datetime
import pytz
import calendar
from ..models import PlanModel, SettingPlanModel, BookModel, NoteModel, WeekdayDefaultModel

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
    object_list = list(PlanModel.objects.filter(month=str(year) + "-" + month3).order_by('time'))
    today = datetime.datetime.today()
    today = datetime.datetime(today.year, today.month, today.day)
    #日にちの過ぎているものを削除
    object_list = [item for item in object_list if (datetime.datetime(int(str(item.date).split('-')[0]), int(str(item.date).split('-')[1]), int(str(item.date).split('-')[2])) - today).days >= 0]
    #プランリストの作成
    c_list_plan = [] #オブジェクトリスト
    plan_list = []
    for c in c_list:
        true_or_false = True
        for item in object_list:
            if str(item.date.day) == c and true_or_false == True:
                c_list_plan.append(item)
                plan_list.append([item])
                true_or_false = False
            elif str(item.date.day) == c and true_or_false == False: #同じ日付がある時
                a = plan_list[-1]
                a2 = [p.plan for p in a]
                if item.plan not in a2:
                    a.append(item)
                plan_list.pop(-1)
                plan_list.append(a)
        if true_or_false:
            c_list_plan.append('')
            plan_list.append('')
    #プランが存在しているプランのみ取得
    plan_exist_list = set(item.plan for item in object_list)
    setting_plan_model = SettingPlanModel.objects.all().order_by('plan_num')
    setting_plan_model_exist = []
    for item in setting_plan_model:
        if item.name in plan_exist_list:
            setting_plan_model_exist.append(item) 
################月曜日と日曜日を非表示にする場合################
    monday = NoteModel.objects.get(num=0).monday
    if monday == 0:
        calendar_list_all = [
            zip(c_list[1:6], c_list_plan[1:6], plan_list[1:6]),
            zip(c_list[8:13], c_list_plan[8:13], plan_list[8:13]),
            zip(c_list[15:20], c_list_plan[15:20], plan_list[15:20]),
            zip(c_list[22:27], c_list_plan[22:27], plan_list[22:27]),
            zip(c_list[29:34], c_list_plan[29:34], plan_list[29:34]),
            zip(c_list[36:41], c_list_plan[36:41], plan_list[36:41])
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
            zip(c_list[0:6], c_list_plan[0:6], plan_list[0:6]),
            zip(c_list[7:13], c_list_plan[7:13], plan_list[7:13]),
            zip(c_list[14:20], c_list_plan[14:20], plan_list[14:20]),
            zip(c_list[21:27], c_list_plan[21:27], plan_list[21:27]),
            zip(c_list[28:34], c_list_plan[28:34], plan_list[28:34]),
            zip(c_list[35:41], c_list_plan[35:41], plan_list[35:41])
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
        'monday': monday,
        'setting_plan_model_exist': setting_plan_model_exist
    }
    return render(request, 'book.html', context)




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
    object_list = list(PlanModel.objects.filter(month=str(year) + "-" + month3).order_by('time'))
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
    setting_plan_model = SettingPlanModel.objects.all().order_by('plan_num')
    if request.method == "POST":
        default = int(request.POST["default_or_not"])
        if default == 0:
            #formの値の取得
            days = request.POST["select_days"]
            select_plan = request.POST["select_plan"]
            plan = list(setting_plan_model)[int(select_plan)].name
            short_plan_name = setting_plan_model.get(name=plan).short_plan_name
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
                plans = PlanModel(date=year_month + "-" + day, month=year_month, plan=plan, short_plan_name=short_plan_name, time=time, plan_num=plan_num, location=location, max_book=max_book)
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
                    short_plan_name =setting_plan_model.get(name=plan).short_plan_name
                    time = item.time
                    plan_num = item.plan_num
                    location = item.location
                    max_book = item.max_book
                    #保存タプルの作成
                    plans = PlanModel(date=year_month + "-" + c, month=year_month, plan=plan, short_plan_name=short_plan_name, time=time, plan_num=plan_num, location=location, max_book=max_book)
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

