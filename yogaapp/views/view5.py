from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from ..models import PlanModel, SettingPlanModel, BookModel
from django.urls import reverse_lazy, reverse
from django_pandas.io import read_frame

#登録者情報
@login_required
def users_detail(request):
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
    