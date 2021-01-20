from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from ..models import BookModel, NoteModel
from django.contrib.auth import authenticate, login, logout

def signupfunc(request):
    if request.method == "POST":
        username = request.POST['username'].replace('　', '').replace(' ', '')
        password = 'password'
        last_name = request.POST['lastname'].replace('　', '').replace(' ', '')
        first_name = request.POST['firstname'].replace('　', '').replace(' ', '')
        email = request.POST['email'].replace('　', '').replace(' ', '')
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


def logoutfunc(request):
    logout(request)
    return redirect('login')    

