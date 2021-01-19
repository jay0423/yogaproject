from django.urls import path
from .views import signupfunc,loginfunc, logoutfunc, bookfunc, confirmfunc, get_yoga_func, cancel_yoga_func, booked_list_func, access_func, info_func
from .views import book_adminfunc, YogaCreate, detail_admin_func, plan_update, PlanDelete, SettingPlanList, SettingPlanUpdate, YogaPlanDelete, users_detail, users_update, signup_admin_func, notefunc, analysis_func, table_func, calendar_dafault_func, weekday_detail_func, weekday_update_func, WeekdayPlanDelete

urlpatterns = [
    path('signup/', signupfunc, name='signup'),
    path('login/', loginfunc, name='login'),
    path('logout/', logoutfunc, name='logout'),
    path('book/<month>', bookfunc, name='book'),
    path('book/<month>/confirm/<date>/', confirmfunc, name='confirm'),
    path('book/<month>/confirm/<date>/get_yoga/<int:pk>', get_yoga_func, name='get_yoga'),
    path('book/<month>/confirm/<date>/cancel_yoga/<int:pk>/<mark>', cancel_yoga_func, name='cancel_yoga'),
    path('booked_list', booked_list_func, name='booked_list'),
    path('access', access_func, name='access'),
    path('info', info_func, name='info'),
    #管理者用
    path('book_admin/<month>', book_adminfunc, name='book_admin'),
    path('book_admin/<month>/detail/<date>/', detail_admin_func, name='detail'),
    path('book_admin/<month>/detail/<date>/update/<int:pk>', plan_update, name='plan_update'),
    path('book_admin/<month>/detail/<date>/delete/<int:pk>', PlanDelete.as_view(), name='plan_delete'),
    path('setting_plan/', SettingPlanList.as_view(), name='setting_plan'),
    path('setting_plan/<int:pk>/detail', SettingPlanUpdate.as_view(), name='setting_plan_update'),
    path('create/', YogaCreate.as_view(), name='create'),
    path('setting_plan/<int:pk>/delete', YogaPlanDelete.as_view(), name='yoga_plan_delete'),
    path('users', users_detail, name='users'), 
    path('users/update/<username>', users_update, name='users_update'), 
    path('analysis/', analysis_func, name='analysis'),
    path('table/', table_func, name='table'),
    path('signup_admin/', signup_admin_func, name='signup_admin'),
    path('note/', notefunc, name='note'),
    path('calendar_default/', calendar_dafault_func, name='calendar_default'),
    path('calendar_default/detail/<weekday>', weekday_detail_func, name='weekday_detail'),
    path('calendar_default/detail/<weekday>/update/<int:pk>', weekday_update_func, name='weekday_update'),
    path('calendar_default/detail/<weekday>/delete/<int:pk>', WeekdayPlanDelete.as_view(), name='weekday_delete'),
]