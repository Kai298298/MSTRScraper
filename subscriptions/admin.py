from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, RequestLog


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'price', 'requests_per_day', 'max_filters', 'can_export', 'can_share']
    list_filter = ['can_export', 'can_share']
    search_fields = ['name', 'display_name']
    ordering = ['price']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'is_active', 'start_date', 'requests_used_today', 'last_request_date']
    list_filter = ['plan', 'is_active', 'start_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['requests_used_today', 'last_request_date']


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'endpoint', 'timestamp', 'success']
    list_filter = ['success', 'timestamp', 'endpoint']
    search_fields = ['user__username', 'endpoint']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
