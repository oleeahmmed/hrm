from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


# ==================== DEPARTMENT MODEL ====================

class Department(models.Model):
    """Department - code/name based, not linked"""
    name = models.CharField(_("Department Name"), max_length=100)
    code = models.CharField(_("Department Code"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ==================== DESIGNATION MODEL ====================

class Designation(models.Model):
    """Designation - code/name based, not linked"""
    name = models.CharField(_("Designation Name"), max_length=100)
    code = models.CharField(_("Designation Code"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    level = models.PositiveIntegerField(_("Level"), default=1)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Designation")
        verbose_name_plural = _("Designations")
        ordering = ['level', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ==================== SHIFT MODEL ====================

class Shift(models.Model):
    """Shift - code/name based, not linked"""
    name = models.CharField(_("Shift Name"), max_length=100)
    code = models.CharField(_("Shift Code"), max_length=50, unique=True)
    start_time = models.TimeField(_("Start Time"))
    end_time = models.TimeField(_("End Time"))
    break_time = models.PositiveIntegerField(_("Break Time (minutes)"), default=60)
    grace_time = models.PositiveIntegerField(_("Grace Time (minutes)"), default=15)
    is_night_shift = models.BooleanField(_("Night Shift"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Shift")
        verbose_name_plural = _("Shifts")
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.start_time}-{self.end_time})"


# ==================== EMPLOYEE MODEL (SIMPLE) ====================

class Employee(models.Model):
    """Simple Employee model - matches attendance by user_id"""
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', _('Active')),
        ('probation', _('Probation')),
        ('suspended', _('Suspended')),
        ('terminated', _('Terminated')),
        ('resigned', _('Resigned'))
    ]
    
    # Basic Information - matches attendance user_id
    user_id = models.CharField(_("User ID"), max_length=50, unique=True, db_index=True)
    employee_id = models.CharField(_("Employee ID"), max_length=50, unique=True)
    
    # Personal Details
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    phone_number = models.CharField(_("Phone"), max_length=20, blank=True)
    
    # Organizational Details (code-based, not linked)
    department_code = models.CharField(_("Department Code"), max_length=50, blank=True)
    designation_code = models.CharField(_("Designation Code"), max_length=50, blank=True)
    shift_code = models.CharField(_("Shift Code"), max_length=50, blank=True)
    
    # Employment Details
    joining_date = models.DateField(_("Joining Date"), blank=True, null=True)
    employment_status = models.CharField(
        _("Employment Status"),
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active'
    )
    
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['employee_id'])
        ]
    
    def __str__(self):
        return f"{self.user_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Get employee's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.employee_id
    
    def get_department(self):
        """Get department by code"""
        if self.department_code:
            try:
                return Department.objects.get(code=self.department_code)
            except Department.DoesNotExist:
                return None
        return None
    
    def get_designation(self):
        """Get designation by code"""
        if self.designation_code:
            try:
                return Designation.objects.get(code=self.designation_code)
            except Designation.DoesNotExist:
                return None
        return None
    
    def get_shift(self):
        """Get shift by code"""
        if self.shift_code:
            try:
                return Shift.objects.get(code=self.shift_code)
            except Shift.DoesNotExist:
                return None
        return None


# ==================== EMPLOYEE PERSONAL INFO MODEL ====================

class EmployeePersonalInfo(models.Model):
    """Employee personal information"""
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
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ]
    
    user_id = models.OneToOneField(
        Employee, 
        on_delete=models.CASCADE, 
        to_field='user_id',
        related_name='personal_info',
        verbose_name=_("Employee")
    )
    
    date_of_birth = models.DateField(_("Date of Birth"), blank=True, null=True)
    gender = models.CharField(_("Gender"), max_length=10, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(_("Blood Group"), max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    marital_status = models.CharField(_("Marital Status"), max_length=20, choices=MARITAL_CHOICES, blank=True)
    nid = models.CharField(_("National ID"), max_length=30, blank=True)
    passport_no = models.CharField(_("Passport Number"), max_length=50, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(_("Emergency Contact Name"), max_length=100, blank=True)
    emergency_contact_phone = models.CharField(_("Emergency Contact Phone"), max_length=20, blank=True)
    emergency_contact_relation = models.CharField(_("Emergency Contact Relation"), max_length=50, blank=True)
    
    # Address
    present_address = models.TextField(_("Present Address"), blank=True)
    permanent_address = models.TextField(_("Permanent Address"), blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Employee Personal Info")
        verbose_name_plural = _("Employee Personal Info")
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - Personal Info"


# ==================== EMPLOYEE EDUCATION MODEL ====================

class EmployeeEducation(models.Model):
    """Employee education information"""
    EDUCATION_LEVEL_CHOICES = [
        ('ssc', _('SSC')),
        ('hsc', _('HSC')),
        ('diploma', _('Diploma')),
        ('bachelor', _('Bachelor')),
        ('master', _('Master')),
        ('phd', _('PhD')),
        ('other', _('Other'))
    ]
    
    user_id = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        to_field='user_id',
        related_name='educations',
        verbose_name=_("Employee")
    )
    
    education_level = models.CharField(_("Education Level"), max_length=20, choices=EDUCATION_LEVEL_CHOICES)
    degree_title = models.CharField(_("Degree Title"), max_length=200)
    institution = models.CharField(_("Institution"), max_length=200)
    passing_year = models.IntegerField(_("Passing Year"), blank=True, null=True)
    result = models.CharField(_("Result/Grade"), max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Employee Education")
        verbose_name_plural = _("Employee Education")
        ordering = ['-passing_year']
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.degree_title}"


# ==================== EMPLOYEE SALARY MODEL ====================

class EmployeeSalary(models.Model):
    """Employee salary information"""
    user_id = models.OneToOneField(
        Employee, 
        on_delete=models.CASCADE, 
        to_field='user_id',
        related_name='salary_info',
        verbose_name=_("Employee")
    )
    
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
    
    effective_from = models.DateField(_("Effective From"), blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Employee Salary")
        verbose_name_plural = _("Employee Salaries")
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - Salary: {self.base_salary}"


# ==================== EMPLOYEE SKILL MODEL ====================

class EmployeeSkill(models.Model):
    """Employee skills"""
    SKILL_LEVEL_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
        ('expert', _('Expert'))
    ]
    
    user_id = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        to_field='user_id',
        related_name='skills',
        verbose_name=_("Employee")
    )
    
    skill_name = models.CharField(_("Skill Name"), max_length=100)
    skill_level = models.CharField(_("Skill Level"), max_length=20, choices=SKILL_LEVEL_CHOICES)
    years_of_experience = models.PositiveIntegerField(_("Years of Experience"), default=0)
    description = models.TextField(_("Description"), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Employee Skill")
        verbose_name_plural = _("Employee Skills")
        unique_together = [['user_id', 'skill_name']]
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.skill_name} ({self.skill_level})"


# ==================== ATTENDANCE MODEL (PROCESSED DAILY RECORDS) ====================

class Attendance(models.Model):
    """Processed daily attendance record"""
    STATUS_CHOICES = [
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('half_day', _('Half Day')),
        ('leave', _('Leave')),
        ('holiday', _('Holiday')),
        ('weekend', _('Weekend'))
    ]
    
    user_id = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        to_field='user_id',
        related_name='attendances',
        verbose_name=_("Employee")
    )
    shift_code = models.CharField(_("Shift Code"), max_length=50, blank=True)
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
    
    # Processing info
    processed_from_logs = models.BooleanField(_("Processed from Logs"), default=False)
    last_processed_at = models.DateTimeField(_("Last Processed At"), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendance Records")
        ordering = ['-date', 'user_id']
        unique_together = [['user_id', 'date']]
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['user_id', 'date']),
            models.Index(fields=['status'])
        ]
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.date} - {self.get_status_display()}"
    
    def get_shift(self):
        """Get shift by code"""
        if self.shift_code:
            try:
                return Shift.objects.get(code=self.shift_code)
            except Shift.DoesNotExist:
                return None
        return None

# ==================== LEAVE TYPE MODEL ====================

class LeaveType(models.Model):
    """Leave type definition"""
    name = models.CharField(_("Leave Type Name"), max_length=100)
    code = models.CharField(_("Leave Type Code"), max_length=50, unique=True)
    max_days = models.PositiveIntegerField(_("Maximum Days"), default=0)
    paid = models.BooleanField(_("Paid"), default=True)
    carry_forward = models.BooleanField(_("Carry Forward"), default=False)
    max_carry_forward_days = models.PositiveIntegerField(_("Max Carry Forward Days"), default=0)
    requires_approval = models.BooleanField(_("Requires Approval"), default=True)
    is_active = models.BooleanField(_("Active"), default=True)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Leave Type")
        verbose_name_plural = _("Leave Types")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ==================== LEAVE BALANCE MODEL ====================

class LeaveBalance(models.Model):
    """Employee leave balance tracking"""
    user_id = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        to_field='user_id',
        related_name='leave_balances',
        verbose_name=_("Employee")
    )
    leave_type_code = models.CharField(_("Leave Type Code"), max_length=50)
    year = models.PositiveIntegerField(_("Year"), default=2024)
    entitled_days = models.FloatField(_("Entitled Days"), default=0)
    used_days = models.FloatField(_("Used Days"), default=0)
    carried_forward_days = models.FloatField(_("Carried Forward Days"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Leave Balance")
        verbose_name_plural = _("Leave Balances")
        ordering = ['user_id', 'leave_type_code']
        unique_together = [['user_id', 'leave_type_code', 'year']]
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.leave_type_code} - {self.year}"
    
    @property
    def remaining_days(self):
        return self.entitled_days + self.carried_forward_days - self.used_days
    
    def get_leave_type(self):
        """Get leave type by code"""
        try:
            return LeaveType.objects.get(code=self.leave_type_code)
        except LeaveType.DoesNotExist:
            return None


# ==================== LEAVE APPLICATION MODEL ====================

class LeaveApplication(models.Model):
    """Leave application"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled'))
    ]
    
    user_id = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        to_field='user_id',
        related_name='leave_applications',
        verbose_name=_("Employee")
    )
    leave_type_code = models.CharField(_("Leave Type Code"), max_length=50)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    total_days = models.FloatField(_("Total Days"), default=0)
    reason = models.TextField(_("Reason"))
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by = models.CharField(_("Approved By"), max_length=100, blank=True)
    approved_at = models.DateTimeField(_("Approved At"), null=True, blank=True)
    rejection_reason = models.TextField(_("Rejection Reason"), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Leave Application")
        verbose_name_plural = _("Leave Applications")
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.leave_type_code} - {self.start_date}"
    
    def get_leave_type(self):
        """Get leave type by code"""
        try:
            return LeaveType.objects.get(code=self.leave_type_code)
        except LeaveType.DoesNotExist:
            return None
    
    def save(self, *args, **kwargs):
        # Auto-calculate total days
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.total_days = delta.days + 1
        super().save(*args, **kwargs)


# ==================== HOLIDAY MODEL ====================

class Holiday(models.Model):
    """Company holiday calendar"""
    name = models.CharField(_("Holiday Name"), max_length=200)
    date = models.DateField(_("Date"))
    is_optional = models.BooleanField(_("Optional Holiday"), default=False)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Holiday")
        verbose_name_plural = _("Holidays")
        ordering = ['-date']
        unique_together = [['name', 'date']]
    
    def __str__(self):
        return f"{self.name} - {self.date}"


# ==================== OVERTIME MODEL ====================

class Overtime(models.Model):
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
    
    user_id = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        to_field='user_id',
        related_name='overtimes',
        verbose_name=_("Employee")
    )
    date = models.DateField(_("Date"), db_index=True)
    shift_code = models.CharField(_("Shift Code"), max_length=50, blank=True)
    
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
    approved_by = models.CharField(_("Approved By"), max_length=100, blank=True)
    approved_at = models.DateTimeField(_("Approved At"), null=True, blank=True)
    
    # Additional info
    remarks = models.TextField(_("Remarks"), blank=True)
    is_paid = models.BooleanField(_("Is Paid"), default=False)
    paid_date = models.DateField(_("Paid Date"), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Overtime")
        verbose_name_plural = _("Overtime Records")
        ordering = ['-date', 'user_id']
        unique_together = [['user_id', 'date']]
        indexes = [
            models.Index(fields=['user_id', 'date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.date} - {self.overtime_hours}h"
    
    def get_shift(self):
        """Get shift by code"""
        if self.shift_code:
            try:
                return Shift.objects.get(code=self.shift_code)
            except Shift.DoesNotExist:
                return None
        return None


# ==================== ATTENDANCE LOG MODEL ====================

class AttendanceLog(models.Model):
    """ZKTeco device theke asha raw punch data"""
    user_id = models.CharField(max_length=50, db_index=True)
    punch_time = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=5, null=True, blank=True)
    verify_type = models.CharField(max_length=5, null=True, blank=True)
    work_code = models.CharField(max_length=10, null=True, blank=True)
    device_sn = models.CharField(max_length=100)
    raw_data = models.TextField()  # Complete raw data save
    
    # Processing er jonno
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-punch_time']
        indexes = [
            models.Index(fields=['user_id', 'punch_time']),
            models.Index(fields=['device_sn']),
            models.Index(fields=['is_processed']),
        ]

    def __str__(self):
        return f"{self.user_id} → {self.punch_time}"
    



# ==================== NOTICE MODEL ====================

class Notice(models.Model):
    """Company notice/announcement"""
    PRIORITY_CHOICES = [
        ('low', _('Low')), 
        ('medium', _('Medium')), 
        ('high', _('High')), 
        ('urgent', _('Urgent'))
    ]
    
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"))
    priority = models.CharField(_("Priority"), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    published_date = models.DateField(_("Published Date"))
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Notice")
        verbose_name_plural = _("Notices")
        ordering = ['-published_date']
    
    def __str__(self):
        return self.title


# ==================== LOCATION MODEL ====================

class Location(models.Model):
    """Geolocation for attendance tracking"""
    name = models.CharField(_("Name"), max_length=100)
    address = models.TextField(_("Address"))
    latitude = models.DecimalField(_("Latitude"), max_digits=10, decimal_places=8)
    longitude = models.DecimalField(_("Longitude"), max_digits=11, decimal_places=8)
    radius = models.DecimalField(_("Radius (km)"), max_digits=5, decimal_places=2)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================== USER LOCATION MODEL ====================

class UserLocation(models.Model):
    """Associates users with locations for attendance tracking"""
    user_id = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        to_field='user_id',
        related_name='user_locations',
        verbose_name=_("Employee")
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='user_locations', verbose_name=_("Location"))
    is_primary = models.BooleanField(_("Is Primary"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("User Location")
        verbose_name_plural = _("User Locations")
        ordering = ['user_id', 'location__name']
        unique_together = [['user_id', 'location']]
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.location.name}"


# ==================== ROSTER MODEL ====================

class Roster(models.Model):
    """Work schedule/roster"""
    name = models.CharField(_("Roster Name"), max_length=200)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    is_active = models.BooleanField(_("Active"), default=True)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Roster")
        verbose_name_plural = _("Rosters")
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


# ==================== ROSTER ASSIGNMENT MODEL ====================

class RosterAssignment(models.Model):
    """Assign employees to roster with default shift"""
    roster = models.ForeignKey(Roster, on_delete=models.CASCADE, related_name='assignments', verbose_name=_("Roster"))
    user_id = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        to_field='user_id',
        related_name='roster_assignments',
        verbose_name=_("Employee")
    )
    shift_code = models.CharField(_("Shift Code"), max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Roster Assignment")
        verbose_name_plural = _("Roster Assignments")
        unique_together = [['roster', 'user_id']]
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.roster.name}"
    
    def get_shift(self):
        """Get shift by code"""
        try:
            return Shift.objects.get(code=self.shift_code)
        except Shift.DoesNotExist:
            return None


# ==================== ROSTER DAY MODEL ====================

class RosterDay(models.Model):
    """Specific day roster"""
    user_id = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        to_field='user_id',
        related_name='roster_days',
        verbose_name=_("Employee")
    )
    date = models.DateField(_("Date"))
    shift_code = models.CharField(_("Shift Code"), max_length=50)
    is_off = models.BooleanField(_("Day Off"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Roster Day")
        verbose_name_plural = _("Roster Days")
        ordering = ['date']
        unique_together = [['user_id', 'date']]
    
    def __str__(self):
        return f"{self.user_id.get_full_name()} - {self.date} - {self.shift_code}"
    
    def get_shift(self):
        """Get shift by code"""
        try:
            return Shift.objects.get(code=self.shift_code)
        except Shift.DoesNotExist:
            return None