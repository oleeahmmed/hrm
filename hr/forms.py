# ==================== hr/forms.py ====================
"""
HR Forms - Report filter forms
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from hr.models import Employee, Shift, Department


class AttendanceReportForm(forms.Form):
    """Attendance Report Filter Form"""
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
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True).order_by('employee_id'),
        required=False,
        empty_label=_('All Employees'),
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Employee')
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label=_('All Departments'),
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Department')
    )
    shift = forms.ModelChoiceField(
        queryset=Shift.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label=_('All Shifts'),
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Shift')
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All Status')),
            ('present', _('Present')),
            ('absent', _('Absent')),
            ('half_day', _('Half Day')),
            ('leave', _('Leave')),
            ('holiday', _('Holiday')),
            ('weekend', _('Weekend')),
        ],
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Status')
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter based on current user's company
        if user and hasattr(user, 'profile'):
            company = user.profile.company
            self.fields['employee'].queryset = Employee.objects.filter(
                company=company,
                is_active=True
            ).order_by('employee_id')
            self.fields['department'].queryset = Department.objects.filter(
                company=company,
                is_active=True
            ).order_by('name')
            self.fields['shift'].queryset = Shift.objects.filter(
                company=company,
                is_active=True
            ).order_by('name')


class PayrollSummaryReportForm(forms.Form):
    """Payroll Summary Report Filter Form"""
    month = forms.ChoiceField(
        required=True,
        choices=[
            ('1', _('January')), ('2', _('February')), ('3', _('March')),
            ('4', _('April')), ('5', _('May')), ('6', _('June')),
            ('7', _('July')), ('8', _('August')), ('9', _('September')),
            ('10', _('October')), ('11', _('November')), ('12', _('December')),
        ],
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Month')
    )
    year = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Year')
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label=_('All Departments'),
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Department')
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Generate year choices (current year and 2 years back)
        from django.utils import timezone
        current_year = timezone.now().year
        year_choices = [(str(y), str(y)) for y in range(current_year - 2, current_year + 1)]
        self.fields['year'].choices = year_choices
        self.fields['year'].initial = str(current_year)
        
        # Set current month as default
        self.fields['month'].initial = str(timezone.now().month)
        
        # Filter based on current user's company
        if user and hasattr(user, 'profile'):
            company = user.profile.company
            self.fields['department'].queryset = Department.objects.filter(
                company=company,
                is_active=True
            ).order_by('name')


class AttendanceSummaryReportForm(forms.Form):
    """Attendance Summary Report Filter Form"""
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
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label=_('All Departments'),
        widget=forms.Select(attrs={
            'class': 'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
        }),
        label=_('Department')
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter based on current user's company
        if user and hasattr(user, 'profile'):
            company = user.profile.company
            self.fields['department'].queryset = Department.objects.filter(
                company=company,
                is_active=True
            ).order_by('name')
