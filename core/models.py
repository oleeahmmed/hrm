from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal


# ==================== BASE MODELS ====================

class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields"""
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    class Meta:
        abstract = True


# ==================== COMPANY MODEL ====================

class Company(TimeStampedModel):
    """Company Model"""
    company_code = models.CharField(_("Company Code"), max_length=20, unique=True)
    name = models.CharField(_("Company Name"), max_length=200)
    
    # Hierarchy
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subsidiaries')
    
    # Address
    address_line1 = models.CharField(_("Address"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    country = models.CharField(_("Country"), max_length=100, default='Bangladesh')
    
    # Contact
    phone_number = models.CharField(_("Phone"), max_length=20, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    
    # Auto-calculated
    level = models.PositiveIntegerField(_("Level"), default=0, editable=False)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.company_code})"
    
    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)


# ==================== USER PROFILE WITH ROLE ====================

class UserProfile(TimeStampedModel):
    """User Profile with Team Role"""
    
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('project_manager', _('Project Manager')),
        ('team_lead', _('Team Lead')),
        ('ui_designer', _('UI Designer')),
        ('ux_designer', _('UX Designer')),
        ('frontend_developer', _('Frontend Developer')),
        ('backend_developer', _('Backend Developer')),
        ('fullstack_developer', _('Full Stack Developer')),
        ('mobile_developer', _('Mobile Developer')),
        ('qa_tester', _('QA Tester')),
        ('devops', _('DevOps Engineer')),
        ('other', _('Other')),
    ]
    
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
    ]
    
    # Core Fields
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey('Company', on_delete=models.PROTECT, related_name='user_profiles')
    
    # Role & Department
    role = models.CharField(_("Role"), max_length=50, choices=ROLE_CHOICES, default='other')
    department = models.CharField(_("Department"), max_length=100, blank=True)
    designation = models.CharField(_("Designation"), max_length=100, blank=True)
    employee_id = models.CharField(_("Employee ID"), max_length=50, blank=True, null=True)
    
    # Personal Info
    phone_number = models.CharField(_("Phone"), max_length=20, blank=True)
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True)
    gender = models.CharField(_("Gender"), max_length=10, choices=GENDER_CHOICES, blank=True)
    
    # Address
    address_line1 = models.CharField(_("Address"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    
    # Professional
    joining_date = models.DateField(_("Joining Date"), blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} ({self.company.name})"
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin' or self.user.is_superuser
    
    def is_project_manager(self):
        """Check if user is project manager"""
        return self.role in ['admin', 'project_manager']
    
    def can_create_project(self):
        """Check if user can create projects"""
        return self.role in ['admin', 'project_manager']
    
    def can_assign_tasks(self):
        """Check if user can assign tasks"""
        return self.role in ['admin', 'project_manager', 'team_lead']


# ==================== PROJECT MODEL ====================

class Project(TimeStampedModel):
    """Project Model - Only Admin/PM can create"""
    
    STATUS_CHOICES = [
        ('planning', _('Planning')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('on_hold', _('On Hold')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]
    
    # Basic Info
    name = models.CharField(_("Project Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    company = models.ForeignKey('Company', on_delete=models.PROTECT, related_name='projects', editable=False)
    
    # Created By (Admin/PM)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_projects',
        editable=False
    )
    
    # Project Manager
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects',
        verbose_name=_("Project Manager")
    )
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(_("Priority"), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Timeline
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    
    # Budget (Optional)
    total_budget = models.DecimalField(
        _("Total Budget"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-start_date']
        unique_together = [['company', 'name']]
    
    def __str__(self):
        return self.name
    
    def get_progress_percentage(self):
        """Calculate project progress"""
        total = self.tasks.count()
        if total == 0:
            return 0
        completed = self.tasks.filter(status='completed').count()
        return round((completed / total) * 100, 2)
    
    def get_team_members(self):
        """Get all team members assigned to this project"""
        return User.objects.filter(
            assigned_tasks__project=self
        ).distinct()


# ==================== TASK MODEL ====================

class Task(TimeStampedModel):
    """Task Model - Team members can only update their own tasks"""
    
    STATUS_CHOICES = [
        ('todo', _('To Do')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('blocked', _('Blocked')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]
    
    # Project & Company (Auto-set)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='tasks')
    company = models.ForeignKey('Company', on_delete=models.PROTECT, related_name='tasks', editable=False)
    
    # Task Info
    title = models.CharField(_("Task Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks',
        verbose_name=_("Assigned To")
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned_by_me',
        verbose_name=_("Assigned By"),
        editable=False
    )
    
    # Status
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(_("Priority"), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Timeline
    due_date = models.DateField(_("Due Date"))
    
    # Hours
    estimated_hours = models.DecimalField(
        _("Estimated Hours"),
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_hours = models.DecimalField(
        _("Actual Hours"),
        max_digits=6,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Blocking
    is_blocked = models.BooleanField(_("Blocked"), default=False)
    blocking_reason = models.TextField(_("Blocking Reason"), blank=True)
    
    # Completion
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ['due_date', '-priority']
    
    def __str__(self):
        assigned = self.assigned_to.username if self.assigned_to else "Unassigned"
        return f"{self.title} - {assigned}"
    
    def save(self, *args, **kwargs):
        # Auto-set company from project
        if self.project_id and not self.company_id:
            self.company = self.project.company
        
        # Auto-set completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status == 'completed' or not self.due_date:
            return False
        return timezone.now().date() > self.due_date
    
    def can_be_edited_by(self, user):
        """Check if user can edit this task"""
        if user.is_superuser:
            return True
        
        if not hasattr(user, 'profile'):
            return False
        
        # Admin/PM/Team Lead can edit all tasks
        if user.profile.role in ['admin', 'project_manager', 'team_lead']:
            return True
        
        # Assigned user can edit their own task (status & hours only)
        return self.assigned_to == user
    
    def can_be_deleted_by(self, user):
        """Check if user can delete this task"""
        if user.is_superuser:
            return True
        
        if not hasattr(user, 'profile'):
            return False
        
        # Only Admin/PM can delete tasks
        return user.profile.role in ['admin', 'project_manager']


# ==================== TASK COMMENT MODEL ====================

class TaskComment(TimeStampedModel):
    """Task Comments - Anyone can comment on their assigned tasks"""
    
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='comments')
    company = models.ForeignKey('Company', on_delete=models.PROTECT, related_name='task_comments', editable=False)
    
    commented_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_comments'
    )
    comment = models.TextField(_("Comment"))
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Task Comment")
        verbose_name_plural = _("Task Comments")
    
    def __str__(self):
        return f"Comment by {self.commented_by.username} on {self.task.title}"
    
    def save(self, *args, **kwargs):
        # Auto-set company from task
        if self.task_id and not self.company_id:
            self.company = self.task.company
        super().save(*args, **kwargs)


# ==================== TASK TIME LOG MODEL ====================

class TaskTimeLog(TimeStampedModel):
    """Track time spent on tasks"""
    
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='time_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_logs')
    
    date = models.DateField(_("Date"), default=timezone.now)
    hours = models.DecimalField(
        _("Hours Worked"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.TextField(_("Work Description"), blank=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = _("Task Time Log")
        verbose_name_plural = _("Task Time Logs")
    
    def __str__(self):
        return f"{self.user.username} - {self.hours}h on {self.task.title}"