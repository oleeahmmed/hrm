from django.contrib import admin
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json
from .models import Task, Project, UserProfile, Company
from .forms import TaskReportForm


class DashboardView(View):
    """Dashboard View with Charts"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        
        # Filter by user's company
        tasks = Task.objects.all()
        projects = Project.objects.all()
        
        if hasattr(request.user, 'profile'):
            company = request.user.profile.company
            tasks = tasks.filter(company=company)
            projects = projects.filter(company=company)
        elif not request.user.is_superuser:
            tasks = tasks.none()
            projects = projects.none()
        
        # Overall Statistics
        total_projects = projects.filter(is_active=True).count()
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        in_progress_tasks = tasks.filter(status='in_progress').count()
        overdue_tasks = tasks.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress', 'blocked']
        ).count()
        
        # Completion rate
        completion_rate = 0
        if total_tasks > 0:
            completion_rate = round((completed_tasks / total_tasks) * 100, 2)
        
        # Hours statistics
        total_estimated_hours = tasks.aggregate(
            total=Sum('estimated_hours')
        )['total'] or Decimal('0.00')
        
        total_actual_hours = tasks.aggregate(
            total=Sum('actual_hours')
        )['total'] or Decimal('0.00')
        
        # Weekly task completion data (last 7 days)
        weekly_completed = []
        weekly_created = []
        weekly_labels = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            completed = tasks.filter(
                completed_at__date=date
            ).count()
            created = tasks.filter(
                created_at__date=date
            ).count()
            weekly_completed.append(completed)
            weekly_created.append(created)
            weekly_labels.append(date.strftime('%d %b'))
        
        # Task status distribution
        status_data = {
            'todo': tasks.filter(status='todo').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'completed': tasks.filter(status='completed').count(),
            'blocked': tasks.filter(status='blocked').count(),
        }
        
        # Project status distribution
        project_status_data = {
            'planning': projects.filter(status='planning').count(),
            'in_progress': projects.filter(status='in_progress').count(),
            'completed': projects.filter(status='completed').count(),
            'on_hold': projects.filter(status='on_hold').count(),
        }
        
        # Top 5 projects by task count
        top_projects = projects.annotate(
            task_count=Count('tasks')
        ).order_by('-task_count')[:5]
        
        project_names = [p.name for p in top_projects]
        project_task_counts = [p.task_count for p in top_projects]
        
        # Recent tasks
        recent_tasks = tasks.select_related(
            'project', 'assigned_to'
        ).order_by('-created_at')[:5]
        
        context = {
            **admin.site.each_context(request),
            'title': 'Dashboard',
            'subtitle': 'Overview of projects and tasks',
            
            # Statistics
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': completion_rate,
            'total_estimated_hours': total_estimated_hours,
            'total_actual_hours': total_actual_hours,
            
            # Chart data
            'weekly_completed': json.dumps(weekly_completed),
            'weekly_created': json.dumps(weekly_created),
            'weekly_labels': json.dumps(weekly_labels),
            'status_data': json.dumps(list(status_data.values())),
            'status_labels': json.dumps(list(status_data.keys())),
            'project_status_data': json.dumps(list(project_status_data.values())),
            'project_status_labels': json.dumps(list(project_status_data.keys())),
            'project_names': json.dumps(project_names),
            'project_task_counts': json.dumps(project_task_counts),
            
            # Recent data
            'recent_tasks': recent_tasks,
        }
        
        return render(request, 'admin/core/dashboard.html', context)


class TaskReportView(View):
    """Task Report View"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = TaskReportForm(user=request.user, data=request.GET or None)
        
        # Default queryset
        tasks = Task.objects.select_related(
            'project', 'assigned_to', 'assigned_by', 'company'
        ).order_by('-created_at')
        
        # Filter by user's company
        if hasattr(request.user, 'profile'):
            tasks = tasks.filter(company=request.user.profile.company)
        elif not request.user.is_superuser:
            tasks = tasks.none()
        
        # Apply filters if form is valid
        if form.is_valid():
            from_date = form.cleaned_data.get('from_date')
            to_date = form.cleaned_data.get('to_date')
            project = form.cleaned_data.get('project')
            assigned_to = form.cleaned_data.get('assigned_to')
            status = form.cleaned_data.get('status')
            
            if from_date:
                tasks = tasks.filter(created_at__date__gte=from_date)
            if to_date:
                tasks = tasks.filter(created_at__date__lte=to_date)
            if project:
                tasks = tasks.filter(project=project)
            if assigned_to:
                tasks = tasks.filter(assigned_to=assigned_to.user)
            if status:
                tasks = tasks.filter(status=status)
        
        # Calculate statistics
        total_tasks = tasks.count()
        todo_count = tasks.filter(status='todo').count()
        in_progress_count = tasks.filter(status='in_progress').count()
        completed_count = tasks.filter(status='completed').count()
        blocked_count = tasks.filter(status='blocked').count()
        
        # Calculate hours
        total_estimated_hours = tasks.aggregate(
            total=Sum('estimated_hours')
        )['total'] or Decimal('0.00')
        
        total_actual_hours = tasks.aggregate(
            total=Sum('actual_hours')
        )['total'] or Decimal('0.00')
        
        # Overdue tasks
        today = timezone.now().date()
        overdue_count = tasks.filter(
            due_date__lt=today,
            status__in=['todo', 'in_progress', 'blocked']
        ).count()
        
        # Completion rate
        completion_rate = 0
        if total_tasks > 0:
            completion_rate = round((completed_count / total_tasks) * 100, 2)
        
        context = {
            **admin.site.each_context(request),
            'title': 'Task Report',
            'subtitle': 'View and filter task records',
            'form': form,
            'tasks': tasks[:200],  # Limit to 200 records
            'total_tasks': total_tasks,
            'todo_count': todo_count,
            'in_progress_count': in_progress_count,
            'completed_count': completed_count,
            'blocked_count': blocked_count,
            'overdue_count': overdue_count,
            'total_estimated_hours': total_estimated_hours,
            'total_actual_hours': total_actual_hours,
            'completion_rate': completion_rate,
        }
        
        return render(request, 'admin/core/task_report.html', context)
