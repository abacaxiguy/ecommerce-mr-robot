from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('', views.ProductList.as_view(), name='list'),
    path('<slug>', views.ProductDetails.as_view(), name='details'),
    path('addCart/', views.AddToCart.as_view(), name='add_cart'),
    path('removeCart/', views.RemoveFromCart.as_view(), name='remove_cart'),
    path('cart/', views.Cart.as_view(), name='cart'),
    path('checkout/', views.CheckOut.as_view(), name='checkout'),
    path('search/', views.Search.as_view(), name='search'),

]
