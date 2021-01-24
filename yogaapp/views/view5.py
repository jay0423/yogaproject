"""
管理者用データ画面の実装．
登録ユーザの情報画面，売り上げやデータ分析画面，テーブル画面の機能の実装．
"""

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

#usersのcsvの作成
def make_users_csv():
    model = User.objects.all()
    columns = ['username', 'first_name', 'last_name', 'email']
    df = read_frame(model, fieldnames=columns)
    #csvファイルで吐き出し
    # df.to_csv('/var/www/yogaproject/static/users.csv', encoding='utf_8_sig')
    df.to_csv('static/users.csv', encoding='utf_8_sig')
    return

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
        make_users_csv()
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


class Analysis:
        
    def __init__(self, post):
        self.post = post
        self.error1 = ""
        self.from_month = ""
        self.last_month = ""
        self.index = 'weekday'
        self.columns = 'plan'
        self.columns2 = "plan"
        self.data = 'rate_of_book'
        self.aggfunc = 'mean'

    def plus_zero(self, num): #1ケタの月の先頭に0を足す
        return '0' + str(num) if len(str(num)) == 1 else str(num)
    
    def make_month_list(self, first_month, last_month):
        first_year = int(first_month[:4])
        last_year = int(last_month[:4])
        month_list = []
        for year in range(first_year, last_year+1):
            for month in range(1, 13):
                month_list.append(str(year) + "-" + str(self.plus_zero(month)))
        month_list = month_list[month_list.index(first_month): month_list.index(last_month)+1]
        return month_list
    
    def make_first_last_month(self):
        first_month = PlanModel.objects.first().month
        last_month = PlanModel.objects.last().month
        return first_month, last_month
    
    def get_post(self, request):
        self.post = True
        self.from_month = request.POST['from_month']
        self.to_month = request.POST['to_month']
        try:
            self.index = request.POST['index']
            self.columns2 = request.POST['columns']
            self.data = request.POST['data']
            self.aggfunc = request.POST['aggfunc']
            self.columns = 'weekday' if self.columns2 == 'weekday2' else self.columns2
        except: #初めて選択するとき．
            pass
    
    #以降データ分析用の処理
    def make_df(self):
        #DataFrameの作成
        month_list = self.make_month_list(self.from_month, self.to_month)
        columns_list = [item.name for item in PlanModel._meta.get_fields()]
        try:
            df = read_frame(PlanModel.objects.filter(month=month_list[0]), fieldnames=columns_list)
        except:
            self.error1 = "error"
            return
        for month in month_list[1:]:
            df = df.append(read_frame(PlanModel.objects.filter(month=month), fieldnames=columns_list))
        df = df.sort_values(['date', 'time'])
        df.reset_index(inplace=True)
        df = df.drop('index', axis=1)
        return df
    
    def add_columns(self, df):
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
        return df
    
    def make_total_price(self, df):
        #月ごとの売上金額の集計
        total_price_per_month = df.groupby("month")[["number_of_people"]].sum()
        total_price_per_month["total_price"] = df.groupby("month")[["total_price"]].sum()
        return total_price_per_month
    
    def round_func(self, pivot_table):
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
        if self.aggfunc == 'mean' or self.aggfunc == 'std' or self.aggfunc == 'median':
            if self.data == 'total_price':
                pivot_table = pivot_table.applymap(round_func2).dropna(axis=1, how='all').dropna(how='all').fillna('')
            else:
                pivot_table = pivot_table.applymap(round_func1).dropna(axis=1, how='all').dropna(how='all').fillna('')
        elif self.aggfunc == 'sum':
            pivot_table = pivot_table.applymap(round_func2).dropna(axis=1, how='all').dropna(how='all').fillna('')
        return pivot_table
        
    def make_pivot_table(self, df):
        #pivot_tableの作成
        print(self.data, self.index, self.columns, self.aggfunc)
        pivot_table = df.pivot_table(self.data, index=self.index, columns=self.columns, aggfunc=self.aggfunc, margins=True)
        #順番の整理用
        if self.index == 'weekday':
            pivot_table = pivot_table.reindex(index=['月', '火', '水', '木', '金', '土', 'All'])
        if self.columns == 'weekday':
            columns_list = ['月', '火', '水', '木', '金', '土', 'All']
        elif self.columns == 'plan':
            columns_list = list(pivot_table.columns)[:-1]
            columns_num_list = []
            for plan in columns_list:
                columns_num_list.append(SettingPlanModel.objects.get(name=plan).plan_num)
            columns_list = [item for _, item in sorted(zip(columns_num_list, columns_list))] + ['All'] 
        pivot_table = pivot_table.reindex(columns=columns_list)
        pivot_table = self.round_func(pivot_table)
        return pivot_table
    
    def make_terms(self):
        #表示する条件
        en_dict = {'weekday': '曜日', 'time': '時間', 'plan': 'プラン', 'rate_of_book': '予約率', 'number_of_people': '予約数', 'total_price': '売上金額', 'mean': '平均値', 'sum': '合計', 'std': '標準偏差', 'median': '中央値'}
        if self.data == 'rate_of_book':
            unit = '%'
        elif self.data == 'number_of_people':
            unit = '-'
        elif self.data == 'total_price':
            unit = '円'
        terms = '{}の{}【{}】｜{}－{}'.format(en_dict[self.data], en_dict[self.aggfunc], unit, en_dict[self.index], en_dict[self.columns])
        return terms
    
    def make_df_to_csv(self, df):
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
        return df_to_csv
    
    def make_rank_book(self, df_to_csv):
        #予約者の頻度ランキング
        booked_people_pivot_table = df_to_csv[df_to_csv.loc[:, 'booked_people_name'] != ''].pivot_table(self.data, index='booked_people_name', columns='plan', aggfunc='count', fill_value=0, margins=True)
        columns_list2 = list(booked_people_pivot_table.columns)
        pivot_list = [booked_people_pivot_table[:-1].loc[:, columns].sort_values(ascending=False) for columns in columns_list2]
        rank2 = [i + 1 for i in range(len(booked_people_pivot_table[:-1].values))]
        pivot_list = [zip(rank2, list(item.index), item.values) for item in pivot_list]
        return columns_list2, pivot_list

    def get_context_data(self):
        df = self.add_columns(self.make_df())
        total_price_per_month = self.make_total_price(df)
        pivot_table = self.make_pivot_table(df)
        columns_list = list(pivot_table.columns)
        terms = self.make_terms()
        df_to_csv = self.make_df_to_csv(df)
        (columns_list2, pivot_list) = self.make_rank_book(df_to_csv)
        context = {
            'post': self.post,
            'error1': self.error1,
            'terms': terms,
            'from_month': self.from_month,
            'to_month': self.to_month,
            'index': self.index,
            'columns': self.columns2,
            'data': self.data,
            'aggfunc': self.aggfunc,
            'total_price_per_month': total_price_per_month,
            'pivot_table': pivot_table,
            'columns_list': columns_list,
            'pivot_list': zip(columns_list2, pivot_list),
            'columns_list2': columns_list2,
            'len_columns_list2': len(columns_list2),
        }
        return context
        
    
#売上やピボットテーブル
@login_required
def analysis_func(request):
    #入力された時の処理
    if request.method == "POST": 
        post = True
        a = Analysis(post)
        a.get_post(request)
        # try:
        (first_month, last_month) = a.make_first_last_month()
        month_list = a.make_month_list(first_month, last_month)
        # except:
        #     context = {
        #         'post': False,
        #         'error1': 'データがありません．',
        #         'month_list': [],
        #         'from_month': '',
        #         'to_month': '',
        #     }
        #     return render(request, 'analysis.html', context)
        if a.error1 == "error": #エラー時
            context = {
                'post': False,
                'error1': '期間が矛盾しています．',
                'month_list': month_list,
                'from_month': '',
                'to_month': '',
            }
            return render(request, 'analysis.html', context)
        try:
            context = a.get_context_data()
            context["month_list"] = month_list
        except: #指定月にデータがないとき
            context = {
                'post': False,
                'error1': '予約者が一人もいません．',
                'month_list': month_list,
                'from_month': '',
                'to_month': '',
            }
        return render(request, 'analysis.html', context)
    else:
        post = False
        a = Analysis(post)
        (first_month, last_month) = a.make_first_last_month()
        month_list = a.make_month_list(first_month, last_month)
        context = {
            'post': False,
            'error1': '',
            'month_list': month_list,
            'from_month': '',
            'to_month': '',
        }
    return render(request, 'analysis.html', context)
        

class Table(Analysis):
    
    def get_context_data(self):
        df = self.add_columns(self.make_df())
        df_to_csv = self.make_df_to_csv(df)
        context = {
            'post': True,
            'error1': self.error1,
            'df': df,
            'from_month': self.from_month,
            'to_month': self.to_month
        }
        return context, df_to_csv
        
#テーブル
@login_required
def table_func(request):
    #入力された時の処理
    if request.method == "POST": 
        post = True
        a = Table(post)
        a.get_post(request)
        # try:
        (first_month, last_month) = a.make_first_last_month()
        month_list = a.make_month_list(first_month, last_month)
        # except:
        #     context = {
        #         'post': False,
        #         'error1': 'データがありません．',
        #         'month_list': [],
        #         'from_month': '',
        #         'to_month': '',
        #     }
        #     return render(request, 'analysis.html', context)
        if a.error1 == "error": #エラー時
            context = {
                'post': False,
                'error1': '期間が矛盾しています．',
                'month_list': month_list,
                'from_month': '',
                'to_month': '',
            }
            return render(request, 'table.html', context)
        try:
            (context, df_to_csv) = a.get_context_data()
            context["month_list"] = month_list
            #csvファイルで吐き出し
            # df_to_csv.to_csv('/var/www/yogaproject/static/table.csv', encoding='utf_8_sig')
            df_to_csv.to_csv('static/table.csv', encoding='utf_8_sig')
        except: #指定月にデータがないとき
            context = {
                'post': False,
                'error1': '予約者が一人もいません．',
                'month_list': month_list,
                'from_month': '',
                'to_month': '',
            }
        return render(request, 'table.html', context)
    else:
        post = False
        a = Analysis(post)
        (first_month, last_month) = a.make_first_last_month()
        month_list = a.make_month_list(first_month, last_month)
        context = {
            'post': post,
            'error1': '',
            'from_month': '',
            'to_month': '',
            'month_list': month_list,
        }
    return render(request, 'table.html', context)