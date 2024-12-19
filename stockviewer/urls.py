# stockviewer/urls.py
from django.contrib import admin
from django.urls import path
from core import views
from core.views import StockListView  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomePageView.as_view(), name='home'),
    path('stocks/', StockListView.as_view(), name='stock_list'),
    path('stocks/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('portfolio/', views.PortfolioView.as_view(), name='portfolio'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/logout/', views.logout_view, name='logout'),
]


