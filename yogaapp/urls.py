from django.urls import path
from .views import signupfunc,loginfunc, logoutfunc, bookfunc, confirmfunc, get_yoga_func, cancel_yoga_func, booked_list_func
from .views import book_adminfunc, YogaCreate, detail_admin_func, PlanUpdate, PlanDelete, SettingPlanList, SettingPlanUpdate, YogaPlanDelete

urlpatterns = [
    path('signup/', signupfunc, name='signup'),
    path('login/', loginfunc, name='login'),
    path('logout/', logoutfunc, name='logout'),
    path('book/<month>', bookfunc, name='book'),
    path('confirm/<date>/', confirmfunc, name='confirm'),
    path('confirm/<date>/get_yoga/<int:pk>', get_yoga_func, name='get_yoga'),
    path('confirm/<date>/cancel_yoga/<int:pk>/<mark>', cancel_yoga_func, name='cancel_yoga'),
    path('booked_list', booked_list_func, name='booked_list'),
    #管理者用
    path('book_admin/<month>', book_adminfunc, name='book_admin'),
    path('detail/<date>/', detail_admin_func, name='detail'),
    path('detail/<date>/update/<int:pk>', PlanUpdate.as_view(), name='plan_update'),
    path('detail/<date>/delete/<int:pk>', PlanDelete.as_view(), name='plan_delete'),
    path('setting_plan/', SettingPlanList.as_view(), name='setting_plan'),
    path('setting_plan/<int:pk>/detail', SettingPlanUpdate.as_view(), name='setting_plan_update'),
    path('create/', YogaCreate.as_view(), name='create'),
    path('setting_plan/<int:pk>/delete', YogaPlanDelete.as_view(), name='yoga_plan_delete'),
]