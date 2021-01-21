from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from ..models import PlanModel, SettingPlanModel, BookModel, NoteModel, WeekdayDefaultModel
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, ListView
from django.urls import reverse_lazy, reverse


#詳細確認
@login_required
def detail_admin_func(request, month, date):
    object_list = list(PlanModel.objects.filter(date=date).order_by('time'))
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
        'month_num': month,
        'date': date,
        'object_plan_name_list': object_plan_name_list,
        'error': error,
    }
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
    
    
#登録者情報
@login_required
def users_detail(request):
    from django_pandas.io import read_frame
    users_list = User.objects.all().order_by('last_name')
    cancel_list = BookModel.objects.all()
    user_df = read_frame(users_list, fieldnames=["last_name", "first_name", "username", "email"])
    user_df["name"] = user_df["last_name"] + user_df["first_name"]
    user2_df = read_frame(cancel_list, fieldnames=["user", "plan", "time_of_cancel"])
    user2_df.index = user2_df["user"]
    user2_df = user2_df.drop("user", axis=1)
    #キャンセル回数を探す
    def find_time_of_cancel(x):
        try:
            return user2_df.at[x, "time_of_cancel"]
        except:
            return 0
    user_df["time_of_cancel"] = user_df["username"].map(find_time_of_cancel)
    context = {
        'df': user_df,
    }
    return render(request, 'users.html', context)


#登録者情報の編集
@login_required
def users_update(request, username):
    object = User.objects.get(username=username)
    if request.method == "POST": 
        new_username = request.POST['username']
        new_lastname = request.POST['last_name']
        new_firstname = request.POST['first_name']
        new_email = request.POST['email']
        #更新
        object.username = new_username
        object.last_name = new_lastname
        object.first_name = new_firstname
        object.email = new_email
        object.save()
####        make_users_csv()
        #ユーザー名が変更されるとき
        if username != new_username:
            user = BookModel.objects.get(user=username)
            user.user = new_username
            user.save()
        return redirect('users')
        
    context = {
        'object': object,
    }
    return render(request, 'users_update.html', context)

# #usersのcsvの作成
# def make_users_csv():
#     from django_pandas.io import read_frame
#     model = User.objects.all()
#     columns = ['username', 'first_name', 'last_name', 'email']
#     df = read_frame(model, fieldnames=columns)
#     #csvファイルで吐き出し
#     # df.to_csv('/var/www/yogaproject/static/users.csv', encoding='utf_8_sig')
#     df.to_csv('static/users.csv', encoding='utf_8_sig')
#     return None
    

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
        # df_to_csv.to_csv('/var/www/yogaproject/static/table.csv', encoding='utf_8_sig')
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
    

# #管理者用サインアップページ
# @login_required
# def signup_admin_func(request):
#     if request.method == "POST":
#         username = request.POST['username'].replace('　', '').replace(' ', '')
#         password = 'password'
#         last_name = request.POST['lastname'].replace('　', '').replace(' ', '')
#         first_name = request.POST['firstname'].replace('　', '').replace(' ', '')
#         email = request.POST['email'].replace('　', '').replace(' ', '')
#         try:
#             user = User.objects.create_user(username, '', password)
#             user.is_active = True
#             user.first_name = first_name
#             user.last_name = last_name
#             user.email = email
#             user.save()
#             user_plan = BookModel.objects.create()
#             user_plan.user = username
#             user_plan.save()
#             make_users_csv()
#             return redirect('signup_admin')
#         except:
#             return render(request, 'signup_admin.html', {'error': 'このユーザーは登録されています'})
#     return render(request, 'signup_admin.html')


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