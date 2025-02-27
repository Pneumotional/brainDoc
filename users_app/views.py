from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
import requests
from .forms import UserRegistrationForm, ProfileForm
from .models import Profile
from documents.models import Document

def home(request):
    return render(request, 'home.html')

def custom_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please complete your profile.')
            # Specify the authentication backend here
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('complete_profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def complete_profile(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('dashboard')
    else:
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'profile.html', {'form': profile_form})

# Update the dashboard view in views.py
@login_required
def dashboard(request):
    profile = request.user.profile
    chat_history = {'messages': [], 'session_id': ''}
    
    # Get last chat session
    try:
        response = requests.get(
            f'http://localhost:8001/sessions/{request.user.id}',
            timeout=2
        )
        if response.status_code == 200:
            sessions = response.json().get('sessions', [])
            if sessions:
                session_id = sessions[-1]
                history_response = requests.get(
                    f'http://localhost:8001/chat_history/{session_id}/{request.user.id}',
                    timeout=2
                )
                if history_response.status_code == 200:
                    chat_history = history_response.json()
    except requests.RequestException:
        pass

    context = {
        'profile': profile,
        'chat_history': chat_history,
        'document_count': Document.objects.filter(user=request.user).count(),  # Filter documents by user
        'documents': Document.objects.filter(user=request.user)               # Filter documents by user
    }
    return render(request, 'dashboard.html', context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to dashboard if user is already logged in

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')