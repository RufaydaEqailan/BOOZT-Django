from django.urls import path
# from ..views.user_views import set_old_users,delete_user
from ..views import user_views,views,modify_user

urlpatterns = [
    path('settestold', views.Set_test_old_users),
    path('add', user_views.add_user),
    path('show', user_views.show_user),
    path('payment', user_views.show_payment_methods),
    path('search', user_views.search_by_value),
    path('setold', user_views.set_old_user),
    path('delete', modify_user.delete_one_user),
    path('modify', modify_user.modify_master_category),
    path('login', user_views.login_user),
    path('logout', user_views.logout_user),
]
