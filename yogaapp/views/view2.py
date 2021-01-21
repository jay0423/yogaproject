from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import datetime
import pytz
import calendar
from ..models import PlanModel, SettingPlanModel, BookModel, NoteModel, WeekdayDefaultModel


class CALENDAR:
            
    def __init__(self, month):
        self.month_num = month # example)-100/0/100/200
        self.month = 1 #仮値，adjust_year_monthを必ず行う．
        self.year = 2021
        self.monday = NoteModel.objects.get(num=0).monday #monday=0：月曜日と日曜日は非表示, monday=1：日曜日は非表示, その他：全曜日を表示

    def adjust_year_month(self):
        #表示月を生成する．
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        self.year = now.year
        #month_numから表示月を生成
        self.month = int(int(self.month_num) / 100 + now.month)
        #翌年以降の調整．
        if self.month > 12:
            self.year += 1
            self.month -= 12
        
    def make_pre_next_month(self):
        #正確な前月，翌月を生成する．(1, 12月時のバグ回避)
        next_month = self.month + 1
        pre_month = self.month - 1
        if next_month > 12:
            next_month -= 12 * abs(int(next_month/12))
        if next_month <= 0:
            next_month += 12 * (abs(int(next_month/12)) + 1)
        if pre_month > 12:
            pre_month -= 12 * abs(int(pre_month/12))
        if pre_month <= 0:
            pre_month += 12 * (abs(int(pre_month/12)) + 1)
        return pre_month, next_month
    
    def get_calendar(self):
        #カレンダーの日付リストを生成する．
        c_str = calendar.month(self.year, self.month)
        c_str = c_str[c_str.find('\n', 25) + 1:]
        c_list = [] #カレンダーの日付リスト
        for i, c in enumerate(c_str.split('\n')[:-1]):
            if i == 0 and len(c.split()) <= 7:
                c_list = c_list + list(' ' * (7 - len(c.split()))) + c.split()
            elif i != 0 and len(c.split()) <= 7:
                c_list = c_list + c.split() + list(' ' * (7 - len(c.split())))
            else:
                c_list += c.split()
        self.c_list = c_list
        return c_list
    
    def make_object_list(self):
        #プランの取得
        month_str = '0' + str(self.month) if len(str(self.month)) == 1 else str(self.month) #1ケタの月の先頭に0を足す
        object_list = list(PlanModel.objects.filter(month=str(self.year) + "-" + month_str).order_by('time'))
        today = datetime.datetime.today()
        today = datetime.datetime(today.year, today.month, today.day)
        #日にちの過ぎているものを削除
        object_list = [item for item in object_list if (datetime.datetime(int(str(item.date).split('-')[0]), int(str(item.date).split('-')[1]), int(str(item.date).split('-')[2])) - today).days >= 0]
        return object_list
    
    def make_plan_list(self, c_list, object_list):
        #contextに使用するc_list_plan(カレンダー表示用のオブジェクトリスト)とplan_list(実際のプラン用のオブジェクト)の作成
        c_list_plan = [] #カレンダー表示用のオブジェクトリスト，同じプランは省略している．
        plan_list = [] #実際のプラン用のオブジェクト，各要素はリストで保存している．
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
        return c_list_plan, plan_list


    def adjust_calendar_list(self, c_list, calendar_list_all):
        if self.monday == 0:
            if c_list[1:6].count(' ') == 5: #1行少ない時用
                calendar_list_all.pop(0)
            if c_list[36:41].count(' ') == 5 or c_list[36:41] == []: #1行少ない時用
                calendar_list_all.pop(-1)
            if c_list[29:34].count(' ') == 5 or c_list[29:34] == []: #1行少ない時用
                calendar_list_all.pop(-1)
        elif self.monday == 1:
            if c_list[0:6].count(' ') == 6: #1行少ない時用
                calendar_list_all.pop(0)
            if c_list[35:41].count(' ') == 6 or c_list[35:41] == []: #1行少ない時用
                calendar_list_all.pop(-1)
            if c_list[28:34].count(' ') == 6 or c_list[28:34] == []: #1行少ない時用
                calendar_list_all.pop(-1)
        else:
            #1つ行が多い月用
            if len(c_list) > 35:
                calendar_list_all.append(zip(c_list[35:], object_list[35:], plan_list[35:]))
        return calendar_list_all
            
    def main(self, c_list, object_list):
        #月曜日と日曜日の有無を考慮して，表示する範囲を設定し，zipで融合させる．
        (c_list_plan, plan_list) = self.make_plan_list(c_list, object_list)
        #月曜日と日曜日を表示しない場合
        if self.monday == 0:
            calendar_list_all = [
                zip(c_list[1:6], c_list_plan[1:6], plan_list[1:6]),
                zip(c_list[8:13], c_list_plan[8:13], plan_list[8:13]),
                zip(c_list[15:20], c_list_plan[15:20], plan_list[15:20]),
                zip(c_list[22:27], c_list_plan[22:27], plan_list[22:27]),
                zip(c_list[29:34], c_list_plan[29:34], plan_list[29:34]),
                zip(c_list[36:41], c_list_plan[36:41], plan_list[36:41])
                ]
        #日曜日を非表示にし，月曜日を表示する場合
        elif self.monday == 1:
            calendar_list_all = [
                zip(c_list[0:6], c_list_plan[0:6], plan_list[0:6]),
                zip(c_list[7:13], c_list_plan[7:13], plan_list[7:13]),
                zip(c_list[14:20], c_list_plan[14:20], plan_list[14:20]),
                zip(c_list[21:27], c_list_plan[21:27], plan_list[21:27]),
                zip(c_list[28:34], c_list_plan[28:34], plan_list[28:34]),
                zip(c_list[35:41], c_list_plan[35:41], plan_list[35:41])
                ]
        ###################月曜日と日曜日を表示する場合###################
        else: #推奨しない．
            calendar_list_all = [
                zip(c_list[:7], object_list[:7], plan_list[:7]),
                zip(c_list[7:14], object_list[7:14], plan_list[7:14]),
                zip(c_list[14:21], object_list[14:21], plan_list[14:21]),
                zip(c_list[21:28], object_list[21:28], plan_list[21:28]),
                zip(c_list[28:35], object_list[28:35], plan_list[28:35])
                ]
        ################################################################
        calendar_list_all = self.adjust_calendar_list(c_list, calendar_list_all)
        return calendar_list_all

    def exist_plan(self, object_list):
        #客用カレンダー画面の下にプランの説明を表示するため
        #プランが存在しているプランのみ取得
        plan_exist_list = set(item.plan for item in object_list)
        setting_plan_model = SettingPlanModel.objects.all().order_by('plan_num')
        setting_plan_model_exist = []
        for item in setting_plan_model:
            if item.name in plan_exist_list:
                setting_plan_model_exist.append(item) 
        return setting_plan_model_exist
        

#顧客用カレンダー画面
@login_required
def bookfunc(request, month):    
    a = CALENDAR(month)
    a.adjust_year_month() #表示月の設定．
    month2 = a.month #表示月の取得
    (pre_month, next_month) = a.make_pre_next_month() #前月と翌月を取得
    c_list = a.get_calendar() #カレンダーリストを生成
    object_list = a.make_object_list() #表示月のプランのオブジェクトを生成
    calendar_list_all = a.main(c_list, object_list) #templatesに送るプランのオブジェクトをまとめたリスト
    monday = a.monday #月曜日，日曜日の有無
    setting_plan_model_exist = a.exist_plan(object_list) #表示月のプランの種類
    
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
    



class CALENDAR_ADMIN(CALENDAR):
        
    def sort_by_time(self, time_list, plan_list):
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
        return new_plan_list
    
    def make_plan_list(self, c_list, object_list):
        #contextに使用するc_list_plan(カレンダー表示用のオブジェクトリスト)とplan_list(実際のプラン用のオブジェクト)の作成
        c_list_plan = [] #カレンダー表示用のオブジェクトリスト，同じプランは省略している．
        plan_list = [] #実際のプラン用のオブジェクト，各要素はリストで保存している．
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
        plan_list = self.sort_by_time(time_list, plan_list)
        return c_list_plan, plan_list
    
    def checkbox_counts(self, c_list):
        #checkboxの総数を算出する
        total_checkbox = 0
        if self.monday == 0:
            new_c_list = c_list[1:6] + c_list[8:13] + c_list[15:20] + c_list[22:27] + c_list[29:34] + c_list[36:41]
        elif self.monday == 1:
            new_c_list = c_list[0:6] + c_list[7:13] + c_list[14:20] + c_list[21:27] + c_list[28:34] + c_list[35:41]
        for c in new_c_list:
            if c != ' ':
                total_checkbox += 1
        return total_checkbox
    
    def djage_default_input(self, object_list):
        #デフォルト入力の必要性を確認
        if len(object_list) == 0:
            default_needs = True
        else:
            default_needs = False
        return default_needs


############################################################
#管理者用
@login_required
def book_adminfunc(request, month):
    a = CALENDAR_ADMIN(month)
    a.adjust_year_month() #表示月の設定．
    month2 = a.month #表示月の取得
    year = a.year
    (pre_month, next_month) = a.make_pre_next_month() #前月と翌月を取得
    c_list = a.get_calendar() #カレンダーリストを生成
    object_list = a.make_object_list() #表示月のプランのオブジェクトを生成
    calendar_list_all = a.main(c_list, object_list) #templatesに送るプランのオブジェクトをまとめたリスト
    monday = a.monday #月曜日，日曜日の有無
    setting_plan_model_exist = a.exist_plan(object_list) #表示月のプランの種類
    
    total_checkbox = a.checkbox_counts(c_list) #チェックボックスの数を取得
    default_needs = a.djage_default_input(object_list)
    
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

