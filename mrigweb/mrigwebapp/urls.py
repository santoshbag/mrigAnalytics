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
from django.urls import path, include
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
    path('mf/<str:symbol>', vw.mf, name='mf'),
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
    path('accounts/', include('allauth.urls')),  # Allauth endpoints
    path('api/auth/login/', vw.login_view,name='logn'),
    path('api/auth/logout/', vw.logout_view, name='logout'),
    path('api/register_user/', vw.register_view, name='register_view'),

    # path('api/auth/', include('rest_framework.urls')),  # DRF login for API testing
    # path('api/auth/', include('dj_rest_auth.urls')),  # For login, logout, etc.
    # path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # For registration
    # path('api/auth/social/', include('allauth.socialaccount.urls')),  # For social login
    path('api/stockdata/<str:symbol>/',vw.stockapi.as_view(), name='apistockdata'),
    path('api/stockdata/<str:symbol>/<str:period>', vw.stockapi.as_view(), name='apistockdata'),
    path('api/stockdata/pv/<str:symbol>/', vw.stockapi.as_view(), name='apistockdata'),
    path('api/stockdata/pv/<str:symbol>/<str:period>', vw.stockapi.as_view(), name='apistockdata'),
    path('api/stockdata/l/<str:symbol>/', vw.stockapi_levels.as_view(), name='apistockdata_levels'),
    path('api/stockdata/oi/<str:symbol>/', vw.stockapi_oitree.as_view(), name='apistockdata_oitree'),
    path('api/stockdata/ta/<str:symbol>/', vw.stockapi_tascreen.as_view(), name='apistockdata_tascreen'),
    path('api/stockpage/<str:symbol>/', vw.stockapi_stockpage.as_view(), name='apistockdata_stockpage'),
    path('api/news/', vw.newsapi.as_view(), name='apinews'),
    path('api/ss/<str:strat>/', vw.stockstrategiesapi.as_view(), name='apistockstrategies'),
    path('api/mf/<str:symbol>/', vw.mfapi_mfpage.as_view(), name='apimf'),
    path('api/mf/', vw.mfapi_mfpage.as_view(), name='apimf'),
    path('api/portfolio/', vw.portfolio_api.as_view(), name='apiportfolio'),
    path('api/mops/<str:symbol>/', vw.marketoptions_api.as_view(), name='apimo'),
    path('api/stockmovers/', vw.stockmovers_api.as_view(), name='apistockmovers'),
    path('api/rates/', vw.rates_api, name='ratesapi'),
    path('api/bonds/', vw.bonds_api, name='bondsapi'),
    path('api/sec_anlys/', vw.sector_analysis_api.as_view(), name='secanlysapi'),
    path('api/stock_pred/<str:symbol>/', vw.stock_predict_api.as_view(), name='stkpedictapi'),
    path('api/portopt/', vw.port_optimize_api.as_view(), name='portoptimization'),
    # Fetch and create portfolios
    path('api/portfolios/', vw.portfolios, name='portfolios'),
    # Manage portfolio items: fetch, add, and delete items
    path('api/portfolios/items/', vw.portfolio_items, name='portfolio_items'),

    # Delete an entire portfolio
    path('api/delete_portfolio/', vw.delete_portfolio, name='delete_portfolio'),
    path('api/csrf/', vw.csrf_token_view, name='csrf_token_view'),

    #Payment URLs
    path('payment/pay/', vw.make_payment, name='make_payment'),

    # path('api/stockdata/<str:symbol>/', vw.stocksapi, name='apistockdata'),

]
