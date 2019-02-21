"""Mrigwebapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
import mrigwebapp.views as vw


urlpatterns = [
    path('home/',vw.home, name='home'),
    path('stock/',vw.stock, name='stock'),
    path('stock/<str:symbol>',vw.stock, name='stock'),
    path('stock1/',vw.stock1, name='stock1'),
    path('os/',vw.os, name='os'),
    path('osa/<str:strategyid>',vw.osa, name='osa'),
    path('ss/',vw.ss, name='ss'),
    path('news/',vw.news, name='news'),
    path('option/<str:opid>',vw.option, name='option'),
]
