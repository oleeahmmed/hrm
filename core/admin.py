from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, TabularInline
from .models import Company, UserProfile, Project, Task, TaskComment, TaskTimeLog


# ==================== COMPANY ADMIN ====================

@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ['company_code', 'name', 'city', 'is_active']
    list_filter = ['is_active', 'country']
    search_fields = ['company_code', 'name', 'city']
    readonly_fields = ['level', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (
                ('company_code', 'name'),
                ('parent', 'is_active'),
            ),
            'classes': ('tab',),
        }),
        (_('📍 Contact'), {
            'fields': (
                ('address_line1', 'city'),
                ('phone_number', 'email'),
                ('country',),
            ),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (
                ('level',),
                ('created_at', 'updated_at'),
            ),
            'classes': ('tab',),
        }),
    )


# ==================== USER PROFILE ADMIN ====================

@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ['user', 'role', 'company', 'department', 'is_active']
    list_filter = ['company', 'role', 'is_active', 'department']
    search_fields = ['user__username', 'user__email', 'employee_id', 'designation']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user', 'company']
    
    fieldsets = (
        (_('📋 Core'), {
            'fields': (
                ('user', 'company'),
                ('role', 'is_active'),
            ),
            'classes': ('tab',),
        }),
        (_('💼 Professional'), {
            'fields': (
                ('designation', 'department'),
                ('employee_id', 'joining_date'),
            ),
            'classes': ('tab',),
        }),
        (_('👤 Personal'), {
            'fields': (
                ('phone_number', 'date_of_birth'),
                ('gender',),
            ),
            'classes': ('tab',),
        }),
        (_('📍 Address'), {
            'fields': (
                ('address_line1', 'city'),
            ),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (
                ('created_at', 'updated_at'),
            ),
            'classes': ('tab',),
        }),
    )


# ==================== TASK INLINE FOR PROJECT ====================

class TaskInline(TabularInline):
    model = Task
    extra = 0
    fields = ['title', 'assigned_to', 'status', 'priority', 'due_date']
    readonly_fields = ['title', 'assigned_to', 'status', 'due_date']
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        """Only Admin/PM can add tasks via inline"""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return request.user.profile.role in ['admin', 'project_manager']
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only Admin/PM can delete tasks"""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return request.user.profile.role in ['admin', 'project_manager']
        return False


# ==================== PROJECT ADMIN ====================

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ['name', 'project_manager', 'status', 'priority', 'start_date', 'end_date', 'progress_display']
    list_filter = ['company', 'status', 'priority', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['company', 'created_by', 'created_at', 'updated_at', 'progress_display']
    autocomplete_fields = ['project_manager']
    inlines = [TaskInline]
    
    fieldsets = (
        (_('📋 Basic Info'), {
            'fields': (
                ('name',),
                ('status', 'priority', 'is_active'),
                ('description',),
            ),
            'classes': ('tab',),
        }),
        (_('👥 Management'), {
            'fields': (
                ('project_manager',),
            ),
            'classes': ('tab',),
        }),
        (_('📅 Timeline'), {
            'fields': (
                ('start_date', 'end_date'),
            ),
            'classes': ('tab',),
        }),
        (_('💰 Budget'), {
            'fields': (
                ('total_budget',),
            ),
            'classes': ('tab',),
        }),
        (_('📊 Progress'), {
            'fields': (
                ('progress_display',),
            ),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (
                ('company', 'created_by'),
                ('created_at', 'updated_at'),
            ),
            'classes': ('tab',),
        }),
    )
    
    def progress_display(self, obj):
        return f"{obj.get_progress_percentage()}%"
    progress_display.short_description = _('Progress')
    
    def save_model(self, request, obj, form, change):
        """Auto-set company and created_by"""
        if not change:
            if hasattr(request.user, 'profile'):
                obj.company = request.user.profile.company
                obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        """Only Admin/PM can create projects"""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return request.user.profile.can_create_project()
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only Admin can delete projects"""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return request.user.profile.is_admin()
        return False
    
    def get_queryset(self, request):
        """Show projects based on role"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'profile'):
            # Admin/PM sees all company projects
            if request.user.profile.role in ['admin', 'project_manager']:
                return qs.filter(company=request.user.profile.company)
            
            # Others see only projects they're assigned to
            return qs.filter(
                company=request.user.profile.company,
                tasks__assigned_to=request.user
            ).distinct()
        
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter project manager choices"""
        if db_field.name == 'project_manager':
            if hasattr(request.user, 'profile'):
                kwargs["queryset"] = User.objects.filter(
                    profile__company=request.user.profile.company,
                    profile__role__in=['admin', 'project_manager', 'team_lead']
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ==================== TASK TIME LOG INLINE ====================

class TaskTimeLogInline(TabularInline):
    model = TaskTimeLog
    extra = 1
    fields = ['date', 'hours', 'description']
    
    def get_queryset(self, request):
        """Show only current user's time logs"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def save_formset(self, request, form, formset, change):
        """Auto-set user for time logs"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TaskTimeLog):
                if not instance.user_id:
                    instance.user = request.user
                instance.save()
        formset.save_m2m()


# ==================== TASK COMMENT INLINE ====================

class TaskCommentInline(TabularInline):
    model = TaskComment
    extra = 1
    fields = ['comment', 'created_at']
    readonly_fields = ['created_at']
    
    def save_formset(self, request, form, formset, change):
        """Auto-set commented_by for comments"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TaskComment):
                if not instance.commented_by_id:
                    instance.commented_by = request.user
                instance.save()
        formset.save_m2m()


# ==================== TASK ADMIN ====================

@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'status', 'priority', 'due_date', 'overdue_display']
    list_filter = ['project', 'status', 'priority', 'assigned_to']
    search_fields = ['title', 'description', 'project__name']
    readonly_fields = ['company', 'assigned_by', 'created_at', 'updated_at', 'overdue_display', 'completed_at']
    autocomplete_fields = ['project', 'assigned_to']
    inlines = [TaskTimeLogInline, TaskCommentInline]
    
    fieldsets = (
        (_('📋 Task Info'), {
            'fields': (
                ('title',),
                ('project', 'assigned_to'),
                ('status', 'priority', 'due_date'),
                ('description',),
            ),
            'classes': ('tab',),
        }),
        (_('⏱️ Time'), {
            'fields': (
                ('estimated_hours', 'actual_hours'),
            ),
            'classes': ('tab',),
        }),
        (_('🚫 Blocking'), {
            'fields': (
                ('is_blocked',),
                ('blocking_reason',),
            ),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (
                ('company', 'assigned_by'),
                ('overdue_display', 'completed_at'),
                ('created_at', 'updated_at'),
            ),
            'classes': ('tab',),
        }),
    )
    
    def overdue_display(self, obj):
        return obj.is_overdue()
    overdue_display.boolean = True
    overdue_display.short_description = _('Overdue')
    
    def save_model(self, request, obj, form, change):
        """Auto-set fields"""
        if not change:
            obj.company = obj.project.company
            obj.assigned_by = request.user
            
            # If team member creates task, auto-assign to themselves
            if hasattr(request.user, 'profile'):
                if request.user.profile.role not in ['admin', 'project_manager', 'team_lead']:
                    obj.assigned_to = request.user
        
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Handle inline formsets"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TaskTimeLog):
                if not instance.user_id:
                    instance.user = request.user
            elif isinstance(instance, TaskComment):
                if not instance.commented_by_id:
                    instance.commented_by = request.user
            instance.save()
        formset.save_m2m()
    
    def has_add_permission(self, request):
        """Everyone can create tasks (for themselves)"""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'profile'):
            return True  # All team members can add tasks
        return False
    
    def has_change_permission(self, request, obj=None):
        """Check if user can edit task"""
        if request.user.is_superuser:
            return True
        
        if obj is None:
            return True
        
        return obj.can_be_edited_by(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """Only Admin/PM can delete tasks"""
        if request.user.is_superuser:
            return True
        
        if obj is None:
            return True
        
        return obj.can_be_deleted_by(request.user)
    
    def get_queryset(self, request):
        """Show tasks based on role"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'profile'):
            # Admin/PM/Team Lead sees all company tasks
            if request.user.profile.role in ['admin', 'project_manager', 'team_lead']:
                return qs.filter(company=request.user.profile.company)
            
            # Team members see only their assigned tasks
            return qs.filter(assigned_to=request.user)
        
        return qs.none()
    
    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly based on role"""
        readonly = list(super().get_readonly_fields(request, obj))
        
        if obj and hasattr(request.user, 'profile'):
            # Team members can only edit their own tasks
            if request.user.profile.role not in ['admin', 'project_manager', 'team_lead']:
                # Check if this is their own task
                if obj.assigned_to == request.user:
                    # They can edit: status, actual_hours, is_blocked, blocking_reason
                    # Everything else is readonly
                    readonly.extend(['title', 'description', 'project', 'assigned_to', 
                                   'priority', 'due_date', 'estimated_hours'])
                else:
                    # Not their task - everything readonly
                    readonly.extend(['title', 'description', 'project', 'assigned_to', 
                                   'status', 'priority', 'due_date', 'estimated_hours',
                                   'actual_hours', 'is_blocked', 'blocking_reason'])
        
        return readonly
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter choices"""
        if db_field.name == 'project':
            if hasattr(request.user, 'profile'):
                kwargs["queryset"] = Project.objects.filter(
                    company=request.user.profile.company,
                    is_active=True
                )
        
        if db_field.name == 'assigned_to':
            if hasattr(request.user, 'profile'):
                # Admin/PM/Team Lead can assign to anyone
                if request.user.profile.role in ['admin', 'project_manager', 'team_lead']:
                    kwargs["queryset"] = User.objects.filter(
                        profile__company=request.user.profile.company,
                        profile__is_active=True
                    )
                else:
                    # Team members can only assign to themselves
                    kwargs["queryset"] = User.objects.filter(id=request.user.id)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ==================== TASK COMMENT ADMIN ====================

@admin.register(TaskComment)
class TaskCommentAdmin(ModelAdmin):
    list_display = ['task', 'commented_by', 'comment_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comment', 'task__title']
    readonly_fields = ['company', 'commented_by', 'created_at', 'updated_at']
    autocomplete_fields = ['task']
    
    fieldsets = (
        (_('💬 Comment'), {
            'fields': (
                ('task',),
                ('comment',),
            ),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (
                ('company', 'commented_by'),
                ('created_at', 'updated_at'),
            ),
            'classes': ('tab',),
        }),
    )
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = _('Comment')
    
    def save_model(self, request, obj, form, change):
        """Auto-set fields"""
        if not change:
            obj.company = obj.task.company
            obj.commented_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Show comments based on role"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'profile'):
            # Admin/PM sees all comments
            if request.user.profile.role in ['admin', 'project_manager']:
                return qs.filter(company=request.user.profile.company)
            
            # Others see only comments on their tasks
            return qs.filter(task__assigned_to=request.user)
        
        return qs.none()


# ==================== TASK TIME LOG ADMIN ====================

@admin.register(TaskTimeLog)
class TaskTimeLogAdmin(ModelAdmin):
    list_display = ['task', 'user', 'date', 'hours', 'description_preview']
    list_filter = ['date', 'user']
    search_fields = ['task__title', 'user__username', 'description']
    readonly_fields = ['user', 'created_at', 'updated_at']
    autocomplete_fields = ['task']
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('⏱️ Time Log'), {
            'fields': (
                ('task', 'date'),
                ('hours',),
                ('description',),
            ),
            'classes': ('tab',),
        }),
        (_('ℹ️ Info'), {
            'fields': (
                ('user',),
                ('created_at', 'updated_at'),
            ),
            'classes': ('tab',),
        }),
    )
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = _('Description')
    
    def save_model(self, request, obj, form, change):
        """Auto-set user"""
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Show time logs based on role"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'profile'):
            # Admin/PM sees all time logs
            if request.user.profile.role in ['admin', 'project_manager']:
                return qs.filter(task__company=request.user.profile.company)
            
            # Others see only their own time logs
            return qs.filter(user=request.user)
        
        return qs.none()
