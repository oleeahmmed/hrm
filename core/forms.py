from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Project, UserProfile


class TaskReportForm(forms.Form):
    """Task Report Filter Form"""
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            'style': 'color-scheme: light dark;'
        }),
        label=_('From Date')
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            'style': 'color-scheme: light dark;'
        }),
        label=_('To Date')
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label=_('All Projects'),
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Project')
    )
    assigned_to = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(is_active=True).select_related('user'),
        required=False,
        empty_label=_('All Team Members'),
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Assigned To')
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All Status')),
            ('todo', _('To Do')),
            ('in_progress', _('In Progress')),
            ('completed', _('Completed')),
            ('blocked', _('Blocked')),
        ],
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Status')
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter projects and users based on current user's company
        if user and hasattr(user, 'profile'):
            company = user.profile.company
            self.fields['project'].queryset = Project.objects.filter(
                company=company,
                is_active=True
            ).order_by('name')
            self.fields['assigned_to'].queryset = UserProfile.objects.filter(
                company=company,
                is_active=True
            ).select_related('user').order_by('user__username')
