import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from decimal import Decimal
from .models import User, ProjectSite, PlantationRecord, CarbonCredit
from .forms import UserRegistrationForm, ProjectSiteForm, PlantationRecordForm
from .forms import LoginForm 
def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')

            # Redirect based on user role
            if user.role == 'ADMIN':
                return redirect('admin_dashboard')
            else:
                return redirect('ngo_dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'registry/login.html', {'form': form})

def home(request):
    total_sites = ProjectSite.objects.count()
    total_records = PlantationRecord.objects.count()
    verified_records = PlantationRecord.objects.filter(verified=True).count()
    total_credits = CarbonCredit.objects.aggregate(Sum('credits_issued'))['credits_issued__sum'] or 0
    
    context = {
        'total_sites': total_sites,
        'total_records': total_records,
        'verified_records': verified_records,
        'total_credits': total_credits,
    }
    return render(request, 'registry/home.html', context)

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Blue Carbon MRV Registry, {user.get_full_name() or user.username}!')
            
            if user.role == 'ADMIN':
                return redirect('admin_dashboard')
            else:
                return redirect('ngo_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.title()}: {error}')
    else:
        form = UserRegistrationForm()
    return render(request, 'registry/register.html', {'form': form})

@login_required
def ngo_dashboard(request):
    if request.user.role not in ['NGO', 'COMMUNITY']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    user_sites = ProjectSite.objects.filter(created_by=request.user)
    user_records = PlantationRecord.objects.filter(uploaded_by=request.user)
    user_credits = CarbonCredit.objects.filter(project_site__created_by=request.user)
    
    context = {
        'user_sites': user_sites,
        'user_records': user_records,
        'user_credits': user_credits,
        'total_credits': user_credits.aggregate(Sum('credits_issued'))['credits_issued__sum'] or 0,
    }
    return render(request, 'registry/ngo_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    all_sites = ProjectSite.objects.all()
    pending_records = PlantationRecord.objects.filter(verified=False)
    all_records = PlantationRecord.objects.all()
    all_credits = CarbonCredit.objects.all()
    
    context = {
        'all_sites': all_sites,
        'pending_records': pending_records,
        'all_records': all_records,
        'all_credits': all_credits,
        'total_credits': all_credits.aggregate(Sum('credits_issued'))['credits_issued__sum'] or 0,
    }
    return render(request, 'registry/admin_dashboard.html', context)

@login_required
def add_project(request):
    if request.user.role not in ['NGO', 'COMMUNITY']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProjectSiteForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Project site added successfully!')
            return redirect('ngo_dashboard')
    else:
        form = ProjectSiteForm()
    return render(request, 'registry/add_project.html', {'form': form})

@login_required
def upload_record(request):
    if request.user.role not in ['NGO', 'COMMUNITY']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PlantationRecordForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.uploaded_by = request.user
            record.save()
            messages.success(request, 'Plantation record uploaded successfully!')
            return redirect('ngo_dashboard')
    else:
        form = PlantationRecordForm(request.user)
    return render(request, 'registry/upload_record.html', {'form': form})

@login_required
def verify_record(request, record_id):
    if request.user.role != 'ADMIN':
        print("Access denied")
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    record = get_object_or_404(PlantationRecord, id=record_id)
    print("check")
    if request.method == 'POST':
        print("Enter")
        print("POST data:", request.POST) 
        action = request.POST.get('action')
        print(action)
        if action == 'approve':
            record.verified = True
            record.verified_by = request.user
            record.verified_date = datetime.datetime.now()
            record.save()
            
            # Generate carbon credits
            credits_amount = calculate_carbon_credits(record)
            CarbonCredit.objects.create(
                project_site=record.project_site,
                plantation_record=record,
                year=record.date_planted.year,
                credits_issued=credits_amount
            )
            
            messages.success(request, f'Record verified and {credits_amount} carbon credits issued!')
        elif action == 'reject':
            messages.info(request, 'Record rejected.')
    
    return redirect('admin_dashboard')

def calculate_carbon_credits(record):
    """Simple calculation for demo purposes"""
    base_credits_per_plant = Decimal('0.5')  # 0.5 credits per plant
    ecosystem_multiplier = {
        'MANGROVE': Decimal('1.5'),
        'SEAGRASS': Decimal('1.2'),
        'MARSH': Decimal('1.0'),
    }
    
    multiplier = ecosystem_multiplier.get(record.project_site.ecosystem_type, Decimal('1.0'))
    total_credits = record.number_of_plants * base_credits_per_plant * multiplier
    
    return round(total_credits, 2)
