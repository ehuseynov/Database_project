from django.shortcuts import render, redirect
from app.db import execute_query, execute_insert_or_update

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = execute_query("SELECT user_id, username FROM users WHERE username=%s AND password=%s;",
                             [username, password], fetchone=True)
        if user:
            # Store user_id in session
            request.session['user_id'] = user[0]
            return redirect('profile')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        mail = request.POST.get('mail')
        
        # Insert user
        execute_insert_or_update("INSERT INTO users (name, username, password, mail) VALUES (%s, %s, %s, %s);",
                                 [name, username, password, mail])
        return redirect('login')
    return render(request, 'signup.html')

def logout_view(request):
    request.session.flush()
    return redirect('home')
