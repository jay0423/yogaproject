"""
サインアップ，管理者用サインアップ，ログイン，ログアウト機能の実装
"""

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from ..models import BookModel, NoteModel
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

class Signup:
    def __init__(self, request):
        self.username = request.POST['username'].replace('　', '').replace(' ', '')
        self.password = 'password'
        self.last_name = request.POST['lastname'].replace('　', '').replace(' ', '')
        self.first_name = request.POST['firstname'].replace('　', '').replace(' ', '')
        self.email = request.POST['email'].replace('　', '').replace(' ', '')
        self.success = False
        
    def signup(self):
        try:
            user = User.objects.create_user(self.username, '', self.password)
            user.is_active = True
            user.first_name = self.first_name
            user.last_name = self.last_name
            user.email = self.email
            user.save()
            #BookModelへのユーザーの登録
            user_plan = BookModel.objects.create()
            user_plan.user = self.username
            user_plan.save()
            self.success = True
        except:
            self.success = False
    
    #usersのcsvの作成
    def make_users_csv(self):
        from django_pandas.io import read_frame
        model = User.objects.all()
        columns = ['username', 'first_name', 'last_name', 'email']
        df = read_frame(model, fieldnames=columns)
        #csvファイルで吐き出し
        # df.to_csv('/var/www/yogaproject/static/users.csv', encoding='utf_8_sig')
        df.to_csv('static/users.csv', encoding='utf_8_sig')
        return

#サインアップページ  
def signupfunc(request):
    if request.method == "POST":
        a = Signup(request)
        a.signup()
        a.make_users_csv()
        if a.success :
            return redirect('login')
        else:
            return render(request, 'signup.html', {'error': 'このユーザーは登録されています'})
    return render(request, 'signup.html')


#管理者用サインアップページ
@login_required
def signup_admin_func(request):
    if request.method == "POST":
        a = Signup(request)
        a.signup()
        a.make_users_csv()
        if a.success :
            return redirect('signup_admin')
        else:
            return render(request, 'signup_admin.html', {'error': 'このユーザーは登録されています'})
    return render(request, 'signup_admin.html')

#ログイン機能の実装
def loginfunc(request):
    item = NoteModel.objects.get(num=0)
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
            context = {
                'memo': item.memo,
                'error': 'このユーザーは登録されていません．'
            }
            return render(request, 'login.html', context)
    context = {
        'memo': item.memo
    }
    return render(request, 'login.html', context)


#ログアウト機能の実装
def logoutfunc(request):
    logout(request)
    return redirect('login')    

