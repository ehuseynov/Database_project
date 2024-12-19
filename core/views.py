from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Stock, Favorite, Portfolio, News
from django.views.generic import ListView
from django.db.models import Q


# Home Page: shows top news and if user logged in, show favorite stocks
class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch some news (e.g., last 5 news items)
        context['news_list'] = News.objects.order_by('-published_at')[:5]

        if self.request.user.is_authenticated:
            # Fetch user favorites
            favorites = Favorite.objects.filter(user=self.request.user).select_related('stock')
            context['favorite_stocks'] = [f.stock for f in favorites]
        else:
            context['favorite_stocks'] = []
        return context


# Detailed stock page
class StockDetailView(DetailView):
    model = Stock
    template_name = 'stock_detail.html'
    context_object_name = 'stock'


# Portfolio page: requires login
@method_decorator(login_required, name='dispatch')
class PortfolioView(LoginRequiredMixin, TemplateView):
    template_name = 'portfolio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch user’s portfolio
        portfolio_items = Portfolio.objects.filter(user=self.request.user).select_related('stock')
        # Calculate total value: sum(quantity * current price)
        total_value = 0
        for item in portfolio_items:
            if item.stock.price:
                total_value += float(item.quantity) * float(item.stock.price)

        context['portfolio_items'] = portfolio_items
        context['total_value'] = total_value
        return context


# Favorites page: requires login
@method_decorator(login_required, name='dispatch')
class FavoritesView(LoginRequiredMixin, TemplateView):
    template_name = 'favorites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorites = Favorite.objects.filter(user=self.request.user).select_related('stock')
        context['favorites'] = [f.stock for f in favorites]
        return context


# User Registration View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect if already logged in

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in the user after registration
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect if already logged in

    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')




class StockListView(ListView):
    model = Stock
    template_name = 'stock_list.html'
    context_object_name = 'stocks'
    paginate_by = 40  # Adjust the number of items per page as needed

    def get_queryset(self):
        queryset = super().get_queryset().order_by('symbol')
        query = self.request.GET.get('q')
        if query:
            # Filter stocks by symbol or name to support searching
            queryset = queryset.filter(
                Q(symbol__icontains=query) | Q(name__icontains=query)
            )
        return queryset

