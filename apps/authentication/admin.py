from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from .models import Profile
from django import forms

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile Details'
    readonly_fields = ('id', 'created_at', 'updated_at', 'profile_status')
    fieldsets = (
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'profile_status'),
            'classes': ('collapse',)
        }),
        ('Basic Information', {
            'fields': ('phone',),
            'classes': ('wide',)
        }),
        ('Academic Information', {
            'fields': (
                'education_level', 
                'field_of_study', 
                'gpa', 
                'target_degree',
                'sat_score',
                'act_score',
                'gre_score',
                'other_test',
                'institution'
            ),
            'classes': ('wide',)
        }),
        ('Demographic Information', {
            'fields': (
                'date_of_birth',
                'gender',
                'ethnicity',
                'citizenship',
                'country'
            ),
            'classes': ('wide',)
        }),
        ('Financial & Background', {
            'fields': (
                'income_bracket',
                'first_generation',
                'has_disability',
                'military_affiliation',
                'special_circumstances'
            ),
            'classes': ('wide',)
        }),
        ('Interests & Goals', {
            'fields': (
                'career_goals',
                'extracurricular_activities',
                'volunteer_experience',
                'special_talents'
            ),
            'classes': ('wide',)
        }),
        ('Preferences', {
            'fields': (
                'preferred_location',
                'study_format',
                'willing_to_relocate',
                'scholarship_types'
            ),
            'classes': ('wide',)
        })
    )

    def profile_status(self, instance):
        if instance.pk:
            completeness = sum(
                1 for field in instance._meta.fields 
                if getattr(instance, field.name) not in [None, '', []]
            )
            total_fields = len(instance._meta.fields) - 3  # exclude id, created_at, updated_at
            percent = int((completeness / total_fields) * 100)
            color = 'green' if percent > 75 else 'orange' if percent > 50 else 'red'
            return format_html(
                '<div style="width:100%; background:lightgray; border-radius:5px;">'
                '<div style="width:{}%; background:{}; color:white; text-align:center; border-radius:5px;">'
                '{}% Complete'
                '</div></div>',
                percent, color, percent
            )
        return "Not saved yet"
    profile_status.short_description = "Completion Status"

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff',
        'profile_exists',
        'profile_completeness'
    )
    list_select_related = ('profile',)

    def profile_exists(self, obj):
        return hasattr(obj, 'profile')
    profile_exists.boolean = True
    profile_exists.short_description = 'Has Profile'

    def profile_completeness(self, obj):
        if hasattr(obj, 'profile'):
            filled = sum(
                1 for field in obj.profile._meta.fields 
                if getattr(obj.profile, field.name) not in [None, '', []]
            )
            total = len(obj.profile._meta.fields) - 3  # exclude metadata fields
            return f"{int((filled/total)*100)}%"
        return "N/A"
    profile_completeness.short_description = 'Profile Complete'

class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

        widgets = {
            'scholarship_types': JSONEditorWidget(options={
                'modes': ['form', 'code', 'tree'],
                'mode': 'form',
                'theme': 'bootstrap'
            }),
            'extracurricular_activities': JSONEditorWidget(options={
                'modes': ['form', 'code', 'tree'],
                'mode': 'form',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    }
                }
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            # Make user field required in admin
            self.fields['user'].required = True

# Standalone Profile Admin for detailed management
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
        
    list_display = (
        'user',
        'phone',
        'education_level',
        'gpa_display',
        'profile_status',
        'created_short'
    )
    list_select_related = ('user',)
    list_filter = (
        'education_level',
        'gender',
        'citizenship',
        'first_generation',
        'created_at'
    )
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'phone',
        'institution'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'profile_status')
    list_select_related = ('user',)
    date_hierarchy = 'created_at'
    fieldsets = ProfileInline.fieldsets  # Reuse the same fieldset organization

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.get_full_name() or obj.user.username
        )
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def save_model(self, request, obj, form, change):
        """Auto-assign user if missing"""
        if not obj.user_id:
            obj.user = request.user  # Assign current admin user
        super().save_model(request, obj, form, change)

    def gpa_display(self, obj):
        return obj.gpa or '-'
    gpa_display.short_description = 'GPA'
    gpa_display.admin_order_field = 'gpa'

    def created_short(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_short.short_description = 'Created'
    created_short.admin_order_field = 'created_at'

    def profile_status(self, obj):
        return ProfileInline.profile_status(self, obj)
    profile_status.short_description = 'Completion'

# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)