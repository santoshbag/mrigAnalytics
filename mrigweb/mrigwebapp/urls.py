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
    path('ia/',vw.ia, name='ia'),
    path('ra/',vw.ra, name='ra'),
    path('softs/',vw.softs, name='softs'),
    path('ds/',vw.ds, name='ds'),
    path('about/',vw.about, name='about'),
    path('market/',vw.market, name='market'),
    path('stock/',vw.stock, name='stock'),
    path('mf/',vw.mf, name='mf'),
    path('stock/<str:symbol>',vw.stock, name='stock'),
    path('folio/',vw.folio, name='folio'),
    # path('folio/folioid/<str:folioid>', vw.folio, name='folio'),
    path('folio/<str:template>', vw.folio, name='folio1'),
    path('stock1/',vw.stock1, name='stock1'),
    path('os/',vw.option_s, name='os'),
    path('osa/<str:strategyid>',vw.osa, name='osa'),
    path('ss/',vw.ss, name='ss'),
    path('screener/',vw.screener, name='screener'),
    path('news/', vw.news, name='news'),
    path('news/<str:newsid>',vw.news, name='news'),
    path('option/<str:opid>',vw.option, name='option'),
    path('ra/rates/',vw.rates, name='rates'),
    path('ra/bonds/',vw.bonds, name='bonds'),
    path('ra/swaps/',vw.swaps, name='swaps'),
    path('ra/options/',vw.options, name='options'),
    path('ra/capsfloors/',vw.capsfloors, name='capsfloors'),
    path('ra/portfolio/',vw.portfolio, name='portfolio'),
        
        
]
