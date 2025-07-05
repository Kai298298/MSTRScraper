from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_email_verified')
    list_filter = ('is_staff', 'is_active', 'profile__email_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_email_verified(self, obj):
        return obj.profile.email_verified if hasattr(obj, 'profile') else False
    get_email_verified.boolean = True
    get_email_verified.short_description = 'E-Mail verifiziert'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_verified', 'onboarding_completed', 'created_at', 'updated_at')
    list_filter = ('email_verified', 'onboarding_completed', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Benutzer', {
            'fields': ('user',)
        }),
        ('Verifikation', {
            'fields': ('email_verified', 'email_verification_token', 'email_verification_sent_at')
        }),
        ('Onboarding', {
            'fields': ('onboarding_completed',)
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
