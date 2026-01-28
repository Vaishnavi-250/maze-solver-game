from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, F
from datetime import datetime, timedelta
import json

from .models import Employee, Attendance
from .forms import EmployeeForm, AttendanceCheckInForm, AttendanceCheckOutForm, AttendanceFilterForm, SignUpForm
from .utils import calculate_distance, is_within_distance, format_distance


def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('attendance:dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    
    context = {'form': form}
    return render(request, 'auth/signup.html', context)


@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('attendance:setup_profile')
    
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(employee=employee, date=today).first()
    
    # Get recent attendances
    recent_attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:7]
    
    # Get this month's statistics
    first_day_of_month = today.replace(day=1)
    month_attendances = Attendance.objects.filter(
        employee=employee,
        date__gte=first_day_of_month,
        date__lte=today
    )
    
    stats = {
        'total_days': month_attendances.count(),
        'present': month_attendances.filter(status='present').count(),
        'late': month_attendances.filter(status='late').count(),
        'absent': month_attendances.filter(status='absent').count(),
        'leave': month_attendances.filter(status='leave').count(),
    }
    
    context = {
        'employee': employee,
        'today_attendance': today_attendance,
        'recent_attendances': recent_attendances,
        'stats': stats,
    }
    
    return render(request, 'attendance/dashboard.html', context)


@login_required
def setup_profile(request):
    """Setup employee profile"""
    employee, created = Employee.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('attendance:dashboard')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {'form': form, 'is_new': created}
    return render(request, 'attendance/setup_profile.html', context)


@login_required
def check_in(request):
    """Check-in view with GPS location"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('attendance:setup_profile')
    
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)
    
    if request.method == 'POST':
        form = AttendanceCheckInForm(request.POST, instance=attendance)
        if form.is_valid():
            instance = form.save(commit=False)
            
            # Get location data
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if latitude and longitude:
                try:
                    instance.check_in_latitude = float(latitude)
                    instance.check_in_longitude = float(longitude)
                    
                    # Calculate distance from office
                    if employee.office_latitude and employee.office_longitude:
                        distance = calculate_distance(
                            employee.office_latitude,
                            employee.office_longitude,
                            instance.check_in_latitude,
                            instance.check_in_longitude
                        )
                        instance.check_in_distance = distance
                except (ValueError, TypeError):
                    pass
            
            # Set check-in time if not provided
            if not instance.check_in_time:
                instance.check_in_time = timezone.now()
            
            instance.save()
            return redirect('attendance:dashboard')
    else:
        if not created and attendance.check_in_time:
            form = AttendanceCheckInForm(instance=attendance)
        else:
            form = AttendanceCheckInForm()
    
    context = {
        'form': form,
        'employee': employee,
        'office_location': {
            'latitude': employee.office_latitude,
            'longitude': employee.office_longitude,
        },
    }
    
    return render(request, 'attendance/check_in.html', context)


@login_required
def check_out(request):
    """Check-out view with GPS location"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('attendance:setup_profile')
    
    today = timezone.now().date()
    attendance = get_object_or_404(Attendance, employee=employee, date=today)
    
    if request.method == 'POST':
        form = AttendanceCheckOutForm(request.POST, instance=attendance)
        if form.is_valid():
            instance = form.save(commit=False)
            
            # Get location data
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if latitude and longitude:
                try:
                    instance.check_out_latitude = float(latitude)
                    instance.check_out_longitude = float(longitude)
                    
                    # Calculate distance from office
                    if employee.office_latitude and employee.office_longitude:
                        distance = calculate_distance(
                            employee.office_latitude,
                            employee.office_longitude,
                            instance.check_out_latitude,
                            instance.check_out_longitude
                        )
                        instance.check_out_distance = distance
                except (ValueError, TypeError):
                    pass
            
            # Set check-out time if not provided
            if not instance.check_out_time:
                instance.check_out_time = timezone.now()
            
            instance.save()
            return redirect('attendance:dashboard')
    else:
        form = AttendanceCheckOutForm(instance=attendance)
    
    context = {
        'form': form,
        'employee': employee,
        'attendance': attendance,
        'office_location': {
            'latitude': employee.office_latitude,
            'longitude': employee.office_longitude,
        },
    }
    
    return render(request, 'attendance/check_out.html', context)


@login_required
def attendance_records(request):
    """View attendance records with filtering"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('attendance:setup_profile')
    
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')
    
    form = AttendanceFilterForm(request.GET)
    
    if form.is_valid():
        if form.cleaned_data.get('date_from'):
            attendances = attendances.filter(date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            attendances = attendances.filter(date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data.get('status'):
            attendances = attendances.filter(status=form.cleaned_data['status'])
    
    context = {
        'attendances': attendances,
        'form': form,
        'format_distance': format_distance,
    }
    
    return render(request, 'attendance/attendance_records.html', context)


@login_required
@require_http_methods(["POST"])
def get_location(request):
    """API endpoint to get user's current GPS location"""
    data = json.loads(request.body)
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')
    
    try:
        employee = Employee.objects.get(user=request.user)
        
        distance = None
        if employee.office_latitude and employee.office_longitude and latitude and longitude:
            distance = calculate_distance(
                employee.office_latitude,
                employee.office_longitude,
                latitude,
                longitude
            )
        
        return JsonResponse({
            'status': 'success',
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': accuracy,
            'distance': distance,
            'office_location': {
                'latitude': employee.office_latitude,
                'longitude': employee.office_longitude,
            } if employee.office_latitude and employee.office_longitude else None,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def attendance_detail(request, attendance_id):
    """View detailed attendance record"""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    # Check if user is authorized
    if attendance.employee.user != request.user:
        return redirect('attendance:dashboard')
    
    context = {
        'attendance': attendance,
        'format_distance': format_distance,
    }
    
    return render(request, 'attendance/attendance_detail.html', context)
