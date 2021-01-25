from django.urls import path
from django.views.generic import RedirectView
from .views.view1 import signupfunc,loginfunc, logoutfunc, signup_admin_func
from .views.view2 import bookfunc, book_adminfunc
from .views.view3 import confirmfunc, get_confirm, cancel_yoga_func, booked_list_func, access_func, info_func
from .views.view4 import detail_admin_func, plan_update, PlanDelete
from .views.view5 import users_detail, users_update, analysis_func, table_func
from .views.view6 import YogaCreate, yoga_create_plan_num, SettingPlanList, SettingPlanUpdate, YogaPlanDelete, notefunc, calendar_dafault_func, weekday_detail_func, weekday_update_func, WeekdayPlanDelete

urlpatterns = [
    path('', RedirectView.as_view(url='login')),
    #views1.py
    path('signup/', signupfunc, name='signup'),
    path('signup_admin/', signup_admin_func, name='signup_admin'),
    path('login/', loginfunc, name='login'),
    path('logout/', logoutfunc, name='logout'),
    #views2.py
    path('book/<month>', bookfunc, name='book'),
    path('book_admin/<month>', book_adminfunc, name='book_admin'),
    #views3.py
    path('book/<month>/confirm/<date>/', confirmfunc, name='confirm'),
    path('book/<month>/confirm/<date>/get_confirm/<int:pk>', get_confirm, name='get_confirm'),
    path('book/<month>/confirm/<date>/cancel_yoga/<int:pk>/<mark>', cancel_yoga_func, name='cancel_yoga'),
    path('booked_list', booked_list_func, name='booked_list'),
    path('access', access_func, name='access'),
    path('info', info_func, name='info'),
    #views4.py
    path('book_admin/<month>/detail/<date>/', detail_admin_func, name='detail'),
    path('book_admin/<month>/detail/<date>/update/<int:pk>', plan_update, name='plan_update'),
    path('book_admin/<month>/detail/<date>/delete/<int:pk>', PlanDelete.as_view(), name='plan_delete'),
    #views5.py
    path('users', users_detail, name='users'), 
    path('users/update/<username>', users_update, name='users_update'), 
    path('analysis/', analysis_func, name='analysis'),
    path('table/', table_func, name='table'),
    #views6.py
    path('setting_plan/', SettingPlanList.as_view(), name='setting_plan'),
    path('setting_plan/<int:pk>/detail', SettingPlanUpdate.as_view(), name='setting_plan_update'),
    path('create/', YogaCreate.as_view(), name='create'),
    path('create/plan_num', yoga_create_plan_num, name='yoga_create_plan_num'),
    path('setting_plan/<int:pk>/delete', YogaPlanDelete.as_view(), name='yoga_plan_delete'),
    path('note/', notefunc, name='note'),
    path('calendar_default/', calendar_dafault_func, name='calendar_default'),
    path('calendar_default/detail/<weekday>', weekday_detail_func, name='weekday_detail'),
    path('calendar_default/detail/<weekday>/update/<int:pk>', weekday_update_func, name='weekday_update'),
    path('calendar_default/detail/<weekday>/delete/<int:pk>', WeekdayPlanDelete.as_view(), name='weekday_delete'),
]