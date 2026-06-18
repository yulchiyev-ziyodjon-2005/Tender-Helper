from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('click/prepare/', views.click_prepare_view, name='click-prepare'),
    path('click/complete/', views.click_complete_view, name='click-complete'),
]
