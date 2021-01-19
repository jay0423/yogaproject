from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
import pytz
import calendar
from .models import PlanModel

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
    if month2 > 12:
        year += 1
        month2 += 1
    c_str = calendar.month(year, month2)
    c_str = c_str[c_str.find('\n', 25) + 1:]
    c_list = []
    for i, c in enumerate(c_str.split('\n')[:-1]):
        if i == 0 and len(c.split()) <= 7:
            c_list = c_list + list(' ' * (7 - len(c.split()))) + c.split()
        elif i != 0 and len(c.split()) <= 7:
            c_list = c_list + c.split() + list(' ' * (7 - len(c.split())))
        else:
            c_list += c.split()
    #新月の追加
    if list(PlanModel.objects.filter(month=month2)) == []:
        make_plan_auto(c_list, year, month2)
    #プランの取得
    object_list = list(PlanModel.objects.filter(month=month2))
    for i in range(c_list[:8].count(' ')):
        object_list.insert(0, ' ')
    for i in range(c_list[-8:].count(' ')):
        object_list.append(' ')
    ################月曜日と日曜日を非表示にしない場合################
    #1つ行が多い月用
    # if len(c_list) > 35:
    #     calendar_list6 = zip(c_list[35:], object_list[35:])
    # else:
    #     calendar_list6 = 0
    # context = {
        # 'month': month,
    #     'calendar_list1': zip(c_list[:7], object_list[:7]),
    #     'calendar_list2': zip(c_list[7:14], object_list[7:14]),
    #     'calendar_list3': zip(c_list[14:21], object_list[14:21]),
    #     'calendar_list4': zip(c_list[21:28], object_list[21:28]),
    #     'calendar_list5': zip(c_list[28:35], object_list[28:35]),
    #     'calendar_list6': calendar_list6,
    # }
    #############################################################
    #2つ行が多い月用
    if c_list[29] != ' ':
        calendar_list5 = zip(c_list[29:34], object_list[29:34])
    else:
        calendar_list5 = zip(c_list[29:34], object_list[29:34])
    context = {
        'month': month,
        'month2': month2,
        'calendar_list1': zip(c_list[1:6], object_list[1:6]),
        'calendar_list2': zip(c_list[8:13], object_list[8:13]),
        'calendar_list3': zip(c_list[15:20], object_list[15:20]),
        'calendar_list4': zip(c_list[22:27], object_list[22:27]),
        'calendar_list5': calendar_list5,
        'calendar_list6': 0,
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
def confirmfunc(request, pk):
    objects = PlanModel.objects.get(pk=pk)
    username = request.user.get_username()
    booked_people_list_1 = objects.booked_people_1.split()
    booked_people_list_2 = objects.booked_people_2.split()
    #既に予約している人手はないかの確認
    if username in booked_people_list_1:
        error_booked1 = '予約済'
    else:
        error_booked1 = 0
    if username in booked_people_list_2:
        error_booked2 = '予約済'
    else:
        error_booked2 = 0
    context = {
        'objects': objects,
        'error_booked1': error_booked1,
        'error_booked2': error_booked2,
    }
    return render(request, 'confirm.html', context)

#plan1の予約者数
def get_yoga1_func(request, pk):
    objects = PlanModel.objects.get(pk=pk)
    if objects.number_of_people_1 == 7:
        context = {
            'objects': objects,        
            'error': '予約人数がいっぱいです　',
        }
        return render(request, 'confirm.html', context)
    else:
        username = request.user.get_username()
        objects.number_of_people_1 += 1
        objects.booked_people_1 += username + ' ' 
        objects.save()        
    return redirect('book', '0')
    
#plan2の予約者数
def get_yoga2_func(request, pk):
    objects = PlanModel.objects.get(pk=pk)
    if objects.number_of_people_2 == 7:
        context = {
            'objects': objects,
            'error2': '予約人数がいっぱいです　',
        }
        return render(request, 'confirm.html', context)
    else:
        username = request.user.get_username()
        objects.number_of_people_2 += 1
        objects.booked_people_2 += username + ' ' 
        objects.save()        
    return redirect('book', '0')

#plan1のキャンセル
def cancel_yoga1_func(request, pk):
    objects = PlanModel.objects.get(pk=pk)
    username = request.user.get_username()
    booked_people_list = objects.booked_people_1.split()
    objects.number_of_people_1 -= 1 #予約人数を減らす
    booked_people_list.remove(username)
    booked_people_str = ''
    for booked_people in booked_people_list:
        booked_people_str += booked_people + ' '
    objects.booked_people_1 = booked_people_str
    objects.save()
    return redirect('book', '0')

#plan2のキャンセル
def cancel_yoga2_func(request, pk):
    objects = PlanModel.objects.get(pk=pk)
    username = request.user.get_username()
    booked_people_list = objects.booked_people_2.split()
    objects.number_of_people_2 -= 1 #予約人数を減らす
    booked_people_list.remove(username)
    booked_people_str = ''
    for booked_people in booked_people_list:
        booked_people_str += booked_people + ' '
    objects.booked_people_2 = booked_people_str
    objects.save()
    return redirect('book', '0')


#管理者用
@login_required
def book_adminfunc(request, month):
    #カレンダーの作製
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    month2 = int(int(month) / 100 + now.month)
    year = now.year
    if month2 > 12:
        year += 1
        month2 += 1
    c_str = calendar.month(year, month2)
    c_str = c_str[c_str.find('\n', 25) + 1:]
    c_list = []
    for i, c in enumerate(c_str.split('\n')[:-1]):
        if i == 0 and len(c.split()) <= 7:
            c_list = c_list + list(' ' * (7 - len(c.split()))) + c.split()
        elif i != 0 and len(c.split()) <= 7:
            c_list = c_list + c.split() + list(' ' * (7 - len(c.split())))
        else:
            c_list += c.split()
    #新月の追加
    if list(PlanModel.objects.filter(month=month2)) == []:
        make_plan_auto(c_list, year, month2)
    #プランの取得
    object_list = list(PlanModel.objects.filter(month=month2))
    for i in range(c_list[:8].count(' ')):
        object_list.insert(0, ' ')
    for i in range(c_list[-8:].count(' ')):
        object_list.append(' ')
    ################月曜日と日曜日を非表示にしない場合################
    #1つ行が多い月用
    # if len(c_list) > 35:
    #     calendar_list6 = zip(c_list[35:], object_list[35:])
    # else:
    #     calendar_list6 = 0
    # context = {
        # 'month': month,
    #     'calendar_list1': zip(c_list[:7], object_list[:7]),
    #     'calendar_list2': zip(c_list[7:14], object_list[7:14]),
    #     'calendar_list3': zip(c_list[14:21], object_list[14:21]),
    #     'calendar_list4': zip(c_list[21:28], object_list[21:28]),
    #     'calendar_list5': zip(c_list[28:35], object_list[28:35]),
    #     'calendar_list6': calendar_list6,
    # }
    #############################################################
    #2つ行が多い月用
    if c_list[29] != ' ':
        calendar_list5 = zip(c_list[29:34], object_list[29:34])
    else:
        calendar_list5 = zip(c_list[29:34], object_list[29:34])
    context = {
        'month': month,
        'month2': month2,
        'calendar_list1': zip(c_list[1:6], object_list[1:6]),
        'calendar_list2': zip(c_list[8:13], object_list[8:13]),
        'calendar_list3': zip(c_list[15:20], object_list[15:20]),
        'calendar_list4': zip(c_list[22:27], object_list[22:27]),
        'calendar_list5': calendar_list5,
        'calendar_list6': 0,
    }
    return render(request, 'book_admin.html', context)