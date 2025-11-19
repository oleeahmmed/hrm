# ==================== hr/models.py ====================
"""
HR Models - Complete HR Management System
All models included with full functionality
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import Company, TimeStampedModel


# ==================== HELPER FUNCTIONS ====================

def get_current_year():
    """Helper function to get current year for model default"""
    return timezone.now().year


# ==================== DEPARTMENT MODEL ====================

class Department(TimeStampedModel):
    """Department within company"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments', verbose_name=_("Company"))
    name = models.CharField(_("Department Name"), max_length=100)
    code = models.CharField(_("Department Code"), max_length=50)
    description = models.TextField(_("Description"), blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        verbose_name=_("Department Head")
    )
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ['company', 'name']
        unique_together = [['company', 'code']]
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


# ==================== DESIGNATION MODEL ====================

class Designation(TimeStampedModel):
    """Job designation/position"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='designations', verbose_name=_("Company"))
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='designations',
        verbose_name=_("Department")
    )
    name = models.CharField(_("Designation Name"), max_length=100)
    code = models.CharField(_("Designation Code"), max_length=50)
    description = models.TextField(_("Description"), blank=True)
    level = models.PositiveIntegerField(_("Level"), default=1)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Designation")
        verbose_name_plural = _("Designations")
        ordering = ['company', 'level', 'name']
        unique_together = [['company', 'code']]
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


# ==================== SHIFT MODEL ====================

class Shift(TimeStampedModel):
    """Work shift definition"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='shifts', verbose_name=_("Company"))
    name = models.CharField(_("Shift Name"), max_length=100)
    code = models.CharField(_("Shift Code"), max_length=50)
    start_time = models.TimeField(_("Start Time"))
    end_time = models.TimeField(_("End Time"))
    break_time = models.PositiveIntegerField(_("Break Time (minutes)"), default=60)
    grace_time = models.PositiveIntegerField(_("Grace Time (minutes)"), default=15)
    is_night_shift = models.BooleanField(_("Night Shift"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Shift")
        verbose_name_plural = _("Shifts")
        ordering = ['company', 'start_time']
        unique_together = [['company', 'code']]
    
    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time}) - {self.company.name}"


# ==================== EMPLOYEE MODEL ====================

class Employee(TimeStampedModel):
    """Employee master record"""
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other'))
    ]
    
    MARITAL_CHOICES = [
        ('single', _('Single')),
        ('married', _('Married')),
        ('divorced', _('Divorced')),
        ('widowed', _('Widowed'))
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', _('Active')),
        ('probation', _('Probation')),
        ('suspended', _('Suspended')),
        ('terminated', _('Terminated')),
        ('resigned', _('Resigned'))
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ]
    
    JOB_TYPE_CHOICES = [
        ('full_time', _('Full-Time')),
        ('part_time', _('Part-Time')),
        ('contract', _('Contract')),
        ('internship', _('Internship'))
    ]
    
    # Basic Information
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees', verbose_name=_("Company"))
    employee_id = models.CharField(_("Employee ID"), max_length=50, unique=True, db_index=True)
    zkteco_id = models.CharField(_("ZKTeco ID"), max_length=50, unique=True, blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
        verbose_name=_("User Account")
    )
    
    # Personal Details
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100, blank=True)
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True)
    gender = models.CharField(_("Gender"), max_length=10, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(_("Blood Group"), max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    marital_status = models.CharField(_("Marital Status"), max_length=20, choices=MARITAL_CHOICES, blank=True)
    nid = models.CharField(_("National ID"), max_length=30, blank=True)
    passport_no = models.CharField(_("Passport Number"), max_length=50, blank=True)
    
    # Contact Information
    email = models.EmailField(_("Email"), blank=True)
    phone_number = models.CharField(_("Phone"), max_length=20, blank=True)
    emergency_contact_name = models.CharField(_("Emergency Contact Name"), max_length=100, blank=True)
    emergency_contact_phone = models.CharField(_("Emergency Contact Phone"), max_length=20, blank=True)
    emergency_contact_relation = models.CharField(_("Emergency Contact Relation"), max_length=50, blank=True)
    
    # Address
    present_address = models.TextField(_("Present Address"), blank=True)
    permanent_address = models.TextField(_("Permanent Address"), blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    
    # Organizational Details
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("Department")
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_("Designation")
    )
    default_shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Default Shift")
    )
    reporting_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_("Reporting To")
    )
    
    # Employment Details
    joining_date = models.DateField(_("Joining Date"), blank=True, null=True)
    confirmation_date = models.DateField(_("Confirmation Date"), blank=True, null=True)
    job_type = models.CharField(_("Job Type"), max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    employment_status = models.CharField(
        _("Employment Status"),
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active'
    )
    resignation_date = models.DateField(_("Resignation Date"), blank=True, null=True)
    termination_date = models.DateField(_("Termination Date"), blank=True, null=True)
    
    # Education
    highest_education = models.CharField(_("Highest Education"), max_length=100, blank=True)
    university = models.CharField(_("University/Institution"), max_length=200, blank=True)
    passing_year = models.IntegerField(_("Passing Year"), blank=True, null=True)
    
    # Salary Information
    base_salary = models.DecimalField(
        _("Base Salary"),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    per_hour_rate = models.DecimalField(
        _("Per Hour Rate"),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    expected_working_hours = models.FloatField(_("Expected Working Hours (Daily)"), default=8.0)
    overtime_rate = models.DecimalField(
        _("Overtime Rate"),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00')
    )
    overtime_grace_minutes = models.IntegerField(_("Overtime Grace Minutes"), default=15)
    
    # Banking Details
    bank_name = models.CharField(_("Bank Name"), max_length=100, blank=True)
    bank_account_no = models.CharField(_("Bank Account No"), max_length=50, blank=True)
    bank_branch = models.CharField(_("Bank Branch"), max_length=100, blank=True)
    payment_method = models.CharField(_("Payment Method"), max_length=20, default="Cash")
    
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        ordering = ['employee_id']
        unique_together = [['company', 'employee_id']]
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['employee_id'])
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Get employee's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.employee_id


# ==================== ZKDEVICE MODEL ====================

class ZkDevice(TimeStampedModel):
    """ZKTeco biometric device"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='zk_devices', verbose_name=_("Company"))
    name = models.CharField(_("Device Name"), max_length=100)
    ip_address = models.GenericIPAddressField(_("IP Address"))
    port = models.PositiveIntegerField(_("Port"), default=4370)
    password = models.CharField(_("Password"), max_length=50, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    last_synced = models.DateTimeField(_("Last Synced"), null=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    
    class Meta:
        verbose_name = _("ZKTeco Device")
        verbose_name_plural = _("ZKTeco Devices")
        ordering = ['company', 'name']
        unique_together = [['company', 'ip_address']]
    
    def __str__(self):
        return f"{self.name} ({self.ip_address}) - {self.company.name}"


# ==================== ATTENDANCE LOG MODEL ====================

class AttendanceLog(TimeStampedModel):
    """Raw attendance punch data from biometric device"""
    SOURCE_CHOICES = [
        ('zk', 'ZKTeco Device'),
        ('manual', 'Manual'),
        ('mobile', 'Mobile')
    ]
    TYPE_CHOICES = [
        ('in', 'Check-in'),
        ('out', 'Check-out')
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendance_logs', verbose_name=_("Company"))
    device = models.ForeignKey(ZkDevice, on_delete=models.CASCADE, verbose_name=_("Device"))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_("Employee"))
    timestamp = models.DateTimeField(_("Timestamp"), db_index=True)
    source_type = models.CharField(_("Source Type"), max_length=10, choices=SOURCE_CHOICES, default='zk')
    attendance_type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES, blank=True)
    status_code = models.IntegerField(_("Status Code"), default=0)
    punch_type = models.CharField(_("Punch Type"), max_length=50, default='UNKNOWN')
    
    # Location tracking
    latitude = models.DecimalField(_("Latitude"), max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(_("Longitude"), max_digits=11, decimal_places=8, null=True, blank=True)
    is_within_radius = models.BooleanField(_("Within Radius"), default=False)
    distance = models.DecimalField(_("Distance (km)"), max_digits=8, decimal_places=2, null=True, blank=True)
    
    device_info = models.TextField(_("Device Info"), blank=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("Attendance Log")
        verbose_name_plural = _("Attendance Logs")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['company', 'employee', 'timestamp']),
            models.Index(fields=['device', 'timestamp'])
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.timestamp}"


# ==================== ATTENDANCE MODEL ====================

class Attendance(TimeStampedModel):
    """Daily attendance summary"""
    STATUS_CHOICES = [
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('half_day', _('Half Day')),
        ('leave', _('Leave')),
        ('holiday', _('Holiday')),
        ('weekend', _('Weekend'))
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendances', verbose_name=_("Company"))
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_("Employee")
    )
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Shift"))
    date = models.DateField(_("Date"), db_index=True)
    check_in_time = models.DateTimeField(_("Check In Time"), null=True, blank=True)
    check_out_time = models.DateTimeField(_("Check Out Time"), null=True, blank=True)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='absent')
    work_hours = models.DecimalField(
        _("Work Hours"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    overtime_hours = models.DecimalField(
        _("Overtime Hours"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    late_minutes = models.IntegerField(_("Late Minutes"), default=0)
    early_out_minutes = models.IntegerField(_("Early Out Minutes"), default=0)
    remarks = models.TextField(_("Remarks"), blank=True)
    
    class Meta:
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendance Records")
        ordering = ['-date', 'employee']
        unique_together = [['company', 'employee', 'date']]
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['employee', 'date'])
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} - {self.get_status_display()}"


# ==================== OVERTIME MODEL ====================

class Overtime(TimeStampedModel):
    """Overtime record for employees"""
    TYPE_CHOICES = [
        ('regular', _('Regular Overtime')),
        ('holiday', _('Holiday Overtime')),
        ('weekend', _('Weekend Overtime')),
        ('night', _('Night Shift Overtime')),
    ]
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('paid', _('Paid')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='overtimes', verbose_name=_("Company"))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtimes', verbose_name=_("Employee"))
    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='overtime_records',
        verbose_name=_("Attendance")
    )
    date = models.DateField(_("Date"), db_index=True)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Shift"))
    
    # Time tracking
    start_time = models.DateTimeField(_("Start Time"), null=True, blank=True)
    end_time = models.DateTimeField(_("End Time"), null=True, blank=True)
    
    # Hours calculation
    overtime_hours = models.DecimalField(_("Overtime Hours"), max_digits=5, decimal_places=2, default=0)
    overtime_type = models.CharField(_("Overtime Type"), max_length=20, choices=TYPE_CHOICES, default='regular')
    
    # Rate and payment
    hourly_rate = models.DecimalField(_("Hourly Rate"), max_digits=10, decimal_places=2, default=0)
    overtime_rate_multiplier = models.DecimalField(
        _("Rate Multiplier"),
        max_digits=4,
        decimal_places=2,
        default=1.5,
        help_text=_("e.g., 1.5 for time-and-a-half, 2.0 for double time")
    )
    total_amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2, default=0)
    
    # Status and approval
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_overtimes',
        verbose_name=_("Approved By")
    )
    approved_at = models.DateTimeField(_("Approved At"), null=True, blank=True)
    
    # Additional info
    remarks = models.TextField(_("Remarks"), blank=True)
    is_paid = models.BooleanField(_("Is Paid"), default=False)
    paid_date = models.DateField(_("Paid Date"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Overtime")
        verbose_name_plural = _("Overtime Records")
        ordering = ['-date', 'employee']
        unique_together = [['company', 'employee', 'date']]
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} - {self.overtime_hours}h"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        if self.overtime_hours and self.hourly_rate:
            self.total_amount = self.overtime_hours * self.hourly_rate * self.overtime_rate_multiplier
        
        # Auto-set approved_at when status changes to approved
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        
        # Auto-set paid status
        if self.status == 'paid':
            self.is_paid = True
            if not self.paid_date:
                self.paid_date = timezone.now().date()
        
        super().save(*args, **kwargs)


# ==================== LEAVE TYPE MODEL ====================

class LeaveType(TimeStampedModel):
    """Leave type definition"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='leave_types', verbose_name=_("Company"))
    name = models.CharField(_("Leave Type Name"), max_length=100)
    code = models.CharField(_("Leave Type Code"), max_length=50)
    max_days = models.PositiveIntegerField(_("Maximum Days"), default=0)
    paid = models.BooleanField(_("Paid"), default=True)
    carry_forward = models.BooleanField(_("Carry Forward"), default=False)
    max_carry_forward_days = models.PositiveIntegerField(_("Max Carry Forward Days"), default=0)
    requires_approval = models.BooleanField(_("Requires Approval"), default=True)
    is_active = models.BooleanField(_("Active"), default=True)
    description = models.TextField(_("Description"), blank=True)
    
    class Meta:
        verbose_name = _("Leave Type")
        verbose_name_plural = _("Leave Types")
        ordering = ['company', 'name']
        unique_together = [['company', 'code']]
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


# ==================== LEAVE BALANCE MODEL ====================

class LeaveBalance(TimeStampedModel):
    """Employee leave balance tracking"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='leave_balances', verbose_name=_("Company"))
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances',
        verbose_name=_("Employee")
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name=_("Leave Type"))
    year = models.PositiveIntegerField(_("Year"), default=get_current_year)
    entitled_days = models.FloatField(_("Entitled Days"), default=0)
    used_days = models.FloatField(_("Used Days"), default=0)
    carried_forward_days = models.FloatField(_("Carried Forward Days"), default=0)
    
    class Meta:
        verbose_name = _("Leave Balance")
        verbose_name_plural = _("Leave Balances")
        ordering = ['employee', 'leave_type']
        unique_together = [['company', 'employee', 'leave_type', 'year']]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type.name} - {self.year}"
    
    @property
    def remaining_days(self):
        return self.entitled_days + self.carried_forward_days - self.used_days
    
    def recalculate_used_days(self):
        """Recalculate used days from approved leave applications"""
        approved_applications = LeaveApplication.objects.filter(
            company=self.company,
            employee=self.employee,
            leave_type=self.leave_type,
            status='approved',
            start_date__year=self.year
        )
        self.used_days = sum(app.total_days for app in approved_applications)
        self.save()
        return self.used_days


# ==================== LEAVE APPLICATION MODEL ====================

class LeaveApplication(TimeStampedModel):
    """Leave application"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled'))
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='leave_applications', verbose_name=_("Company"))
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_applications',
        verbose_name=_("Employee")
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, verbose_name=_("Leave Type"))
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    total_days = models.FloatField(_("Total Days"), default=0)
    reason = models.TextField(_("Reason"))
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        verbose_name=_("Approved By")
    )
    approved_at = models.DateTimeField(_("Approved At"), null=True, blank=True)
    rejection_reason = models.TextField(_("Rejection Reason"), blank=True)
    
    class Meta:
        verbose_name = _("Leave Application")
        verbose_name_plural = _("Leave Applications")
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type.name} - {self.start_date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total days
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.total_days = delta.days + 1
        
        # Auto-set approved_at when status changes to approved
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        
        # Auto-set company from employee
        if self.employee_id and not self.company_id:
            self.company = self.employee.company
        
        super().save(*args, **kwargs)


# ==================== HOLIDAY MODEL ====================

class Holiday(TimeStampedModel):
    """Company holiday calendar"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='holidays', verbose_name=_("Company"))
    name = models.CharField(_("Holiday Name"), max_length=200)
    date = models.DateField(_("Date"))
    is_optional = models.BooleanField(_("Optional Holiday"), default=False)
    description = models.TextField(_("Description"), blank=True)
    
    class Meta:
        verbose_name = _("Holiday")
        verbose_name_plural = _("Holidays")
        ordering = ['-date']
        unique_together = [['company', 'date']]
    
    def __str__(self):
        return f"{self.name} - {self.date} - {self.company.name}"


# ==================== ROSTER MODEL ====================

class Roster(TimeStampedModel):
    """Work schedule/roster"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='rosters', verbose_name=_("Company"))
    name = models.CharField(_("Roster Name"), max_length=200)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    is_active = models.BooleanField(_("Active"), default=True)
    description = models.TextField(_("Description"), blank=True)
    
    class Meta:
        verbose_name = _("Roster")
        verbose_name_plural = _("Rosters")
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date}) - {self.company.name}"


# ==================== ROSTER ASSIGNMENT MODEL ====================

class RosterAssignment(TimeStampedModel):
    """Assign employees to roster with default shift"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='roster_assignments', verbose_name=_("Company"))
    roster = models.ForeignKey(Roster, on_delete=models.CASCADE, related_name='assignments', verbose_name=_("Roster"))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='roster_assignments', verbose_name=_("Employee"))
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name=_("Default Shift"))
    
    class Meta:
        verbose_name = _("Roster Assignment")
        verbose_name_plural = _("Roster Assignments")
        unique_together = [['roster', 'employee']]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.roster.name}"
    
    def save(self, *args, **kwargs):
        # Auto-set company from roster
        if self.roster_id and not self.company_id:
            self.company = self.roster.company
        super().save(*args, **kwargs)


# ==================== ROSTER DAY MODEL ====================

class RosterDay(TimeStampedModel):
    """Specific day roster"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='roster_days', verbose_name=_("Company"))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='roster_days', verbose_name=_("Employee"))
    date = models.DateField(_("Date"))
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name=_("Shift"))
    is_off = models.BooleanField(_("Day Off"), default=False)
    
    class Meta:
        verbose_name = _("Roster Day")
        verbose_name_plural = _("Roster Days")
        ordering = ['date']
        unique_together = [['company', 'employee', 'date']]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} - {self.shift.name}"


# ==================== NOTICE ====================

class Notice(TimeStampedModel):
    """Company notice/announcement"""
    PRIORITY_CHOICES = [
        ('low', _('Low')), 
        ('medium', _('Medium')), 
        ('high', _('High')), 
        ('urgent', _('Urgent'))
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notices', verbose_name=_("Company"))
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"))
    priority = models.CharField(_("Priority"), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    published_date = models.DateField(_("Published Date"))
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Notice")
        verbose_name_plural = _("Notices")
        ordering = ['-published_date']
    
    def __str__(self):
        return f"{self.title} - {self.company.name}"


# ==================== ATTENDANCE PROCESSOR CONFIGURATION ====================

class AttendanceProcessorConfiguration(TimeStampedModel):
    """Attendance Processor configuration for all attendance processing rules"""
    BREAK_DEDUCTION_CHOICES = [
        ('fixed', _('Fixed')), 
        ('proportional', _('Proportional'))
    ]
    SHIFT_PRIORITY_CHOICES = [
        ('least_break', _('Least Break Time')),
        ('shortest_duration', _('Shortest Duration')),
        ('alphabetical', _('Alphabetical')),
        ('highest_score', _('Highest Score'))
    ]
    OVERTIME_METHOD_CHOICES = [
        ('shift_based', _('Shift Based')),
        ('employee_based', _('Employee Based')),
        ('fixed_hours', _('Fixed Hours'))
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='attendance_configs', verbose_name=_("Company"))
    name = models.CharField(_("Configuration Name"), max_length=100, default="Default Configuration")
    is_active = models.BooleanField(_("Active"), default=True)
    
    # Basic Attendance Settings
    grace_minutes = models.PositiveIntegerField(_("Grace Minutes"), default=15, help_text=_("Late arrival grace period in minutes"))
    early_out_threshold_minutes = models.PositiveIntegerField(_("Early Out Threshold (minutes)"), default=30, help_text=_("Minutes before end time to consider as early departure"))
    overtime_start_after_minutes = models.PositiveIntegerField(_("Overtime Start After (minutes)"), default=15, help_text=_("Minutes after scheduled end time to start overtime calculation"))
    minimum_overtime_minutes = models.PositiveIntegerField(_("Minimum Overtime Minutes"), default=60, help_text=_("Minimum overtime duration to be eligible for overtime pay"))
    
    # Weekend Configuration
    weekend_friday = models.BooleanField(_("Friday Weekend"), default=True)
    weekend_saturday = models.BooleanField(_("Saturday Weekend"), default=False)
    weekend_sunday = models.BooleanField(_("Sunday Weekend"), default=False)
    weekend_monday = models.BooleanField(_("Monday Weekend"), default=False)
    weekend_tuesday = models.BooleanField(_("Tuesday Weekend"), default=False)
    weekend_wednesday = models.BooleanField(_("Wednesday Weekend"), default=False)
    weekend_thursday = models.BooleanField(_("Thursday Weekend"), default=False)
    
    # Break Time Configuration
    default_break_minutes = models.PositiveIntegerField(_("Default Break Time (minutes)"), default=60, help_text=_("Default break time if shift doesn't specify"))
    use_shift_break_time = models.BooleanField(_("Use Shift Break Time"), default=True, help_text=_("Use shift-specific break time instead of default"))
    break_deduction_method = models.CharField(_("Break Deduction Method"), max_length=20, choices=BREAK_DEDUCTION_CHOICES, default='fixed', help_text=_("Method to calculate break time deduction"))
    
    # Enhanced Rule 1: Minimum Working Hours Rule
    enable_minimum_working_hours_rule = models.BooleanField(_("Enable Minimum Working Hours Rule"), default=False, help_text=_("Convert present to absent if working hours below threshold"))
    minimum_working_hours_for_present = models.FloatField(_("Minimum Working Hours for Present"), default=4.0, help_text=_("Minimum hours required to mark as present"))
    
    # Enhanced Rule 2: Working Hours Half Day Rule
    enable_working_hours_half_day_rule = models.BooleanField(_("Enable Working Hours Half Day Rule"), default=False, help_text=_("Convert to half day based on working hours range"))
    half_day_minimum_hours = models.FloatField(_("Half Day Minimum Hours"), default=4.0, help_text=_("Minimum hours for half day qualification"))
    half_day_maximum_hours = models.FloatField(_("Half Day Maximum Hours"), default=6.0, help_text=_("Maximum hours for half day qualification"))
    
    # Enhanced Rule 3: Both In and Out Time Requirement
    require_both_in_and_out = models.BooleanField(_("Require Both In and Out Time"), default=False, help_text=_("Mark as absent if either check-in or check-out is missing"))
    
    # Enhanced Rule 4: Maximum Working Hours Rule
    enable_maximum_working_hours_rule = models.BooleanField(_("Enable Maximum Working Hours Rule"), default=False, help_text=_("Flag records with excessive working hours"))
    maximum_allowable_working_hours = models.FloatField(_("Maximum Allowable Working Hours"), default=16.0, help_text=_("Maximum allowed working hours per day"))
    
    # Enhanced Rule 5: Dynamic Shift Detection
    enable_dynamic_shift_detection = models.BooleanField(_("Enable Dynamic Shift Detection"), default=False, help_text=_("Automatically detect shift based on attendance pattern"))
    dynamic_shift_tolerance_minutes = models.PositiveIntegerField(_("Dynamic Shift Tolerance (minutes)"), default=30, help_text=_("Tolerance in minutes for shift pattern matching"))
    multiple_shift_priority = models.CharField(_("Multiple Shift Priority"), max_length=20, choices=SHIFT_PRIORITY_CHOICES, default='least_break', help_text=_("Priority method when multiple shifts match"))
    dynamic_shift_fallback_to_default = models.BooleanField(_("Dynamic Shift Fallback to Default"), default=True, help_text=_("Use employee's default shift if dynamic detection fails"))
    dynamic_shift_fallback_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='fallback_configs', verbose_name=_("Fallback Shift"), help_text=_("Fixed shift to use if dynamic detection fails and no default shift"))
    
    # Enhanced Rule 6: Shift Grace Time
    use_shift_grace_time = models.BooleanField(_("Use Shift-Specific Grace Time"), default=False, help_text=_("Use grace time from shift instead of global grace time"))
    
    # Enhanced Rule 7: Consecutive Absence Flagging
    enable_consecutive_absence_flagging = models.BooleanField(_("Enable Consecutive Absence Flagging"), default=False, help_text=_("Flag employees with consecutive absences as termination risk"))
    consecutive_absence_termination_risk_days = models.PositiveIntegerField(_("Consecutive Absence Risk Days"), default=5, help_text=_("Number of consecutive absent days to flag as termination risk"))
    
    # Enhanced Rule 8: Early Out Flagging
    enable_max_early_out_flagging = models.BooleanField(_("Enable Max Early Out Flagging"), default=False, help_text=_("Flag employees with excessive early departures"))
    max_early_out_threshold_minutes = models.PositiveIntegerField(_("Max Early Out Threshold (minutes)"), default=120, help_text=_("Minutes of early departure to consider excessive"))
    max_early_out_occurrences = models.PositiveIntegerField(_("Max Early Out Occurrences"), default=3, help_text=_("Number of early departures in a month to flag"))
    
    # Overtime Configuration
    overtime_calculation_method = models.CharField(_("Overtime Calculation Method"), max_length=20, choices=OVERTIME_METHOD_CHOICES, default='employee_based', help_text=_("Method to calculate overtime"))
    holiday_overtime_full_day = models.BooleanField(_("Holiday Overtime Full Day"), default=True, help_text=_("Count all holiday working hours as overtime"))
    weekend_overtime_full_day = models.BooleanField(_("Weekend Overtime Full Day"), default=True, help_text=_("Count all weekend working hours as overtime"))
    late_affects_overtime = models.BooleanField(_("Late Arrival Affects Overtime"), default=False, help_text=_("Reduce overtime if employee arrives late"))
    separate_ot_break_time = models.PositiveIntegerField(_("Separate OT Break Time (minutes)"), default=0, help_text=_("Additional break time to deduct from overtime"))
    
    # Employee-Specific Settings
    use_employee_specific_grace = models.BooleanField(_("Use Employee Specific Grace"), default=True, help_text=_("Use employee-specific grace time if available"))
    use_employee_specific_overtime = models.BooleanField(_("Use Employee Specific Overtime"), default=True, help_text=_("Use employee-specific overtime settings if available"))
    use_employee_expected_hours = models.BooleanField(_("Use Employee Expected Hours"), default=True, help_text=_("Use employee-specific expected working hours"))
    
    # Advanced Rules
    late_to_absent_days = models.PositiveIntegerField(_("Late to Absent Days"), default=3, help_text=_("Convert late to absent after consecutive late days"))
    holiday_before_after_absent = models.BooleanField(_("Holiday Before/After Absent"), default=True, help_text=_("Consider attendance around holidays for absence rules"))
    weekend_before_after_absent = models.BooleanField(_("Weekend Before/After Absent"), default=True, help_text=_("Consider attendance around weekends for absence rules"))
    require_holiday_presence = models.BooleanField(_("Require Holiday Presence"), default=False, help_text=_("Require attendance on designated working holidays"))
    include_holiday_analysis = models.BooleanField(_("Include Holiday Analysis"), default=True, help_text=_("Include holiday patterns in attendance analysis"))
    holiday_buffer_days = models.PositiveIntegerField(_("Holiday Buffer Days"), default=1, help_text=_("Days before/after holiday to consider for analysis"))
    
    # Display Options
    show_absent_employees = models.BooleanField(_("Show Absent Employees"), default=True, help_text=_("Include absent employees in reports"))
    show_leave_employees = models.BooleanField(_("Show Leave Employees"), default=True, help_text=_("Include employees on leave in reports"))
    show_holiday_status = models.BooleanField(_("Show Holiday Status"), default=True, help_text=_("Show holiday information in reports"))
    include_roster_info = models.BooleanField(_("Include Roster Info"), default=True, help_text=_("Include roster information in attendance records"))
    
    class Meta:
        verbose_name = _("Attendance Processor Configuration")
        verbose_name_plural = _("Attendance Processor Configurations")
        ordering = ['-is_active', 'name']
        unique_together = [['company', 'name']]
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} - {self.company.name} ({status})"
    
    @property
    def weekend_days(self):
        """Get weekend days as a list of integers (0=Monday, 6=Sunday)"""
        days = []
        if self.weekend_monday:
            days.append(0)
        if self.weekend_tuesday:
            days.append(1)
        if self.weekend_wednesday:
            days.append(2)
        if self.weekend_thursday:
            days.append(3)
        if self.weekend_friday:
            days.append(4)
        if self.weekend_saturday:
            days.append(5)
        if self.weekend_sunday:
            days.append(6)
        return days
    
    def get_config_dict(self):
        """Convert model instance to dictionary for processor"""
        return {
            # Basic settings
            'grace_minutes': self.grace_minutes,
            'early_out_threshold_minutes': self.early_out_threshold_minutes,
            'overtime_start_after_minutes': self.overtime_start_after_minutes,
            'minimum_overtime_minutes': self.minimum_overtime_minutes,
            'weekend_days': self.weekend_days,
            # Break time
            'default_break_minutes': self.default_break_minutes,
            'use_shift_break_time': self.use_shift_break_time,
            'break_deduction_method': self.break_deduction_method,
            # Enhanced rules
            'enable_minimum_working_hours_rule': self.enable_minimum_working_hours_rule,
            'minimum_working_hours_for_present': self.minimum_working_hours_for_present,
            'enable_working_hours_half_day_rule': self.enable_working_hours_half_day_rule,
            'half_day_minimum_hours': self.half_day_minimum_hours,
            'half_day_maximum_hours': self.half_day_maximum_hours,
            'require_both_in_and_out': self.require_both_in_and_out,
            'enable_maximum_working_hours_rule': self.enable_maximum_working_hours_rule,
            'maximum_allowable_working_hours': self.maximum_allowable_working_hours,
            # Dynamic shift detection
            'enable_dynamic_shift_detection': self.enable_dynamic_shift_detection,
            'dynamic_shift_tolerance_minutes': self.dynamic_shift_tolerance_minutes,
            'multiple_shift_priority': self.multiple_shift_priority,
            'dynamic_shift_fallback_to_default': self.dynamic_shift_fallback_to_default,
            'dynamic_shift_fallback_shift_id': self.dynamic_shift_fallback_shift_id,
            # Shift grace time
            'use_shift_grace_time': self.use_shift_grace_time,
            # Consecutive absence
            'enable_consecutive_absence_flagging': self.enable_consecutive_absence_flagging,
            'consecutive_absence_termination_risk_days': self.consecutive_absence_termination_risk_days,
            # Early out flagging
            'enable_max_early_out_flagging': self.enable_max_early_out_flagging,
            'max_early_out_threshold_minutes': self.max_early_out_threshold_minutes,
            'max_early_out_occurrences': self.max_early_out_occurrences,
            # Overtime configuration
            'overtime_calculation_method': self.overtime_calculation_method,
            'holiday_overtime_full_day': self.holiday_overtime_full_day,
            'weekend_overtime_full_day': self.weekend_overtime_full_day,
            'late_affects_overtime': self.late_affects_overtime,
            'separate_ot_break_time': self.separate_ot_break_time,
            # Employee-specific settings
            'use_employee_specific_grace': self.use_employee_specific_grace,
            'use_employee_specific_overtime': self.use_employee_specific_overtime,
            'use_employee_expected_hours': self.use_employee_expected_hours,
            # Advanced rules
            'late_to_absent_days': self.late_to_absent_days,
            'holiday_before_after_absent': self.holiday_before_after_absent,
            'weekend_before_after_absent': self.weekend_before_after_absent,
            'require_holiday_presence': self.require_holiday_presence,
            'include_holiday_analysis': self.include_holiday_analysis,
            'holiday_buffer_days': self.holiday_buffer_days,
            # Display options
            'show_absent_employees': self.show_absent_employees,
            'show_leave_employees': self.show_leave_employees,
            'show_holiday_status': self.show_holiday_status,
            'include_roster_info': self.include_roster_info,
        }
    
    def save(self, *args, **kwargs):
        # Ensure only one active configuration per company
        if self.is_active:
            AttendanceProcessorConfiguration.objects.filter(
                company=self.company, 
                is_active=True
            ).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_config(cls, company):
        """Get active configuration for a company"""
        try:
            return cls.objects.filter(company=company, is_active=True).first()
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_config_dict_for_company(cls, company):
        """Get configuration dictionary for a company"""
        config = cls.get_active_config(company)
        if config:
            return config.get_config_dict()
        else:
            # Return default configuration
            return cls.get_default_config()
    
    @classmethod
    def get_default_config(cls):
        """Get default configuration dictionary"""
        return {
            'grace_minutes': 15,
            'early_out_threshold_minutes': 30,
            'overtime_start_after_minutes': 15,
            'minimum_overtime_minutes': 60,
            'weekend_days': [4],  # Friday
            'default_break_minutes': 60,
            'use_shift_break_time': True,
            'break_deduction_method': 'fixed',
            'enable_minimum_working_hours_rule': False,
            'minimum_working_hours_for_present': 4.0,
            'enable_working_hours_half_day_rule': False,
            'half_day_minimum_hours': 4.0,
            'half_day_maximum_hours': 6.0,
            'require_both_in_and_out': False,
            'enable_maximum_working_hours_rule': False,
            'maximum_allowable_working_hours': 16.0,
            'enable_dynamic_shift_detection': False,
            'dynamic_shift_tolerance_minutes': 30,
            'multiple_shift_priority': 'least_break',
            'dynamic_shift_fallback_to_default': True,
            'dynamic_shift_fallback_shift_id': None,
            'use_shift_grace_time': False,
            'enable_consecutive_absence_flagging': False,
            'consecutive_absence_termination_risk_days': 5,
            'enable_max_early_out_flagging': False,
            'max_early_out_threshold_minutes': 120,
            'max_early_out_occurrences': 3,
            'overtime_calculation_method': 'employee_based',
            'holiday_overtime_full_day': True,
            'weekend_overtime_full_day': True,
            'late_affects_overtime': False,
            'separate_ot_break_time': 0,
            'use_employee_specific_grace': True,
            'use_employee_specific_overtime': True,
            'use_employee_expected_hours': True,
            'late_to_absent_days': 3,
            'holiday_before_after_absent': True,
            'weekend_before_after_absent': True,
            'require_holiday_presence': False,
            'include_holiday_analysis': True,
            'holiday_buffer_days': 1,
            'show_absent_employees': True,
            'show_leave_employees': True,
            'show_holiday_status': True,
            'include_roster_info': True,
        }


# ==================== LOCATION ====================

class Location(TimeStampedModel):
    """Geolocation for attendance tracking"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='locations', verbose_name=_("Company"))
    name = models.CharField(_("Name"), max_length=100)
    address = models.TextField(_("Address"))
    latitude = models.DecimalField(_("Latitude"), max_digits=10, decimal_places=8)
    longitude = models.DecimalField(_("Longitude"), max_digits=11, decimal_places=8)
    radius = models.DecimalField(_("Radius (km)"), max_digits=5, decimal_places=2)
    is_active = models.BooleanField(_("Is Active"), default=True)
    
    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        ordering = ['company', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


class UserLocation(TimeStampedModel):
    """Associates users with locations for attendance tracking"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_locations', verbose_name=_("Company"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_locations', verbose_name=_("User"))
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='user_locations', verbose_name=_("Location"))
    is_primary = models.BooleanField(_("Is Primary"), default=False)
    
    class Meta:
        verbose_name = _("User Location")
        verbose_name_plural = _("User Locations")
        ordering = ['company', 'user__username', 'location__name']
        unique_together = [['company', 'user', 'location']]
    
    def __str__(self):
        return f"{self.user.username} - {self.location.name} - {self.company.name}"        