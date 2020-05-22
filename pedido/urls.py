from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('pay/<int:pk>', views.PayOrder.as_view(), name='pay'),
    path('finish/', views.FinishOrder.as_view(), name='finish'),
    path('lists/', views.ListOrders.as_view(), name='lists'),
    path('details/<int:pk>', views.OrderDetails.as_view(), name='details'),
    path('GAMEOVER/', views.Over.as_view(), name="over"),
]
