from django.urls import path
from app.views.home_views import home_view
from app.views.auth_views import login_view, logout_view, signup_view
from app.views.profile_views import profile_view
from app.views.portfolio_views import portfolio_view

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path('profile/', profile_view, name='profile'),
    path('portfolio/', portfolio_view, name='portfolio'),
]