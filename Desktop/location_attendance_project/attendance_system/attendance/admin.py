from django.contrib import admin
from .models import Employee, Attendance


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_user_name', 'department', 'position', 'phone')
    list_filter = ('department', 'position', 'created_at')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Employee Details', {
            'fields': ('employee_id', 'phone', 'department', 'position')
        }),
        ('Office Location', {
            'fields': ('office_latitude', 'office_longitude'),
            'description': 'Set the office coordinates for distance calculation'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_user_name.short_description = 'Name'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'get_check_in_time', 'get_check_out_time', 'status', 'check_in_distance')
    list_filter = ('status', 'date', 'employee__department')
    search_fields = ('employee__employee_id', 'employee__user__first_name', 'employee__user__last_name')
    ordering = ('-date', '-check_in_time')
    
    fieldsets = (
        ('Employee & Date', {
            'fields': ('employee', 'date', 'status')
        }),
        ('Check In', {
            'fields': ('check_in_time', 'check_in_latitude', 'check_in_longitude', 'check_in_distance')
        }),
        ('Check Out', {
            'fields': ('check_out_time', 'check_out_latitude', 'check_out_longitude', 'check_out_distance')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_check_in_time(self, obj):
        if obj.check_in_time:
            return obj.check_in_time.strftime('%H:%M:%S')
        return '-'
    get_check_in_time.short_description = 'Check In'
    
    def get_check_out_time(self, obj):
        if obj.check_out_time:
            return obj.check_out_time.strftime('%H:%M:%S')
        return '-'
    get_check_out_time.short_description = 'Check Out'
