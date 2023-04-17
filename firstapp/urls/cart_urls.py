from django.urls import path
from ..views import  cart_views,modify_cart

urlpatterns = [
    path('setold', cart_views.set_old_carts),
    path('cleanup', cart_views.delete_carts),
    path('delete', modify_cart.delete_one_cart),
    # path('modify', modify_cart.modify_master_category),
    path('show', cart_views.show_carts),
    path('status', cart_views.show_by_status),
    path('search', cart_views.search_by_value),
    path('add', cart_views.add_cart)

]
