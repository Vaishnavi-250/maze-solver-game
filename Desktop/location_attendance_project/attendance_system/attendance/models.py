from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Employee(models.Model):
    """Model to store employee information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    office_latitude = models.FloatField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        help_text="Office location latitude for distance calculation"
    )
    office_longitude = models.FloatField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        help_text="Office location longitude for distance calculation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"


class Attendance(models.Model):
    """Model to store attendance records with GPS location tracking"""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('leave', 'Leave'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    
    # GPS Location data for check-in
    check_in_latitude = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    check_in_longitude = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    
    # GPS Location data for check-out
    check_out_latitude = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    check_out_longitude = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    
    # Distance calculations
    check_in_distance = models.FloatField(
        null=True, 
        blank=True,
        help_text="Distance from office during check-in (in meters)"
    )
    check_out_distance = models.FloatField(
        null=True, 
        blank=True,
        help_text="Distance from office during check-out (in meters)"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        ordering = ['-date', '-check_in_time']
        unique_together = [['employee', 'date']]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} ({self.status})"

    @property
    def total_hours(self):
        """Calculate total hours worked"""
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            return round(delta.total_seconds() / 3600, 2)
        return None
