from django.urls import path
from .views import signupfunc,loginfunc, logoutfunc, bookfunc, confirmfunc, get_yoga1_func, get_yoga2_func, cancel_yoga1_func, cancel_yoga2_func
from .views import book_adminfunc

urlpatterns = [
    path('signup/', signupfunc, name='signup'),
    path('login/', loginfunc, name='login'),
    path('logout/', logoutfunc, name='logout'),
    path('book/<month>', bookfunc, name='book'),
    path('confirm/<int:pk>/', confirmfunc, name='confirm'),
    path('confirm/<int:pk>/get_yoga1', get_yoga1_func, name='get_yoga1'),
    path('confirm/<int:pk>/get_yoga2', get_yoga2_func, name='get_yoga2'),
    path('confirm/<int:pk>/cancel_yoga1', cancel_yoga1_func, name='cancel_yoga1'),
    path('confirm/<int:pk>/cancel_yoga2', cancel_yoga2_func, name='cancel_yoga2'),
    #管理者用
    path('book_admin/<month>', book_adminfunc, name='book_admin'),
]