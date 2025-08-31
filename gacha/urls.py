# gacha/urls.py
from django.urls import path
from . import views

app_name = 'gacha'

urlpatterns = [
    path('', views.index, name='index'),         # 入力フォーム
    path('result/', views.result, name='result') # 結果表示
]