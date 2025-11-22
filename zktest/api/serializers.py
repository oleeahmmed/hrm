from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from ..models import (
    Department, Designation, Shift, Employee, EmployeePersonalInfo,
    EmployeeEducation, EmployeeSalary, EmployeeSkill, AttendanceLog,
    Attendance, LeaveType, LeaveBalance, LeaveApplication, Holiday,
    Overtime, Notice, Location, UserLocation, Roster, RosterAssignment,
    RosterDay
)


# ==================== BASIC MODELS SERIALIZERS ====================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


# ==================== EMPLOYEE SERIALIZERS ====================

class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    department_name = serializers.SerializerMethodField()
    designation_name = serializers.SerializerMethodField()
    shift_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = '__all__'
    
    def get_department_name(self, obj):
        dept = obj.get_department()
        return dept.name if dept else None
    
    def get_designation_name(self, obj):
        desig = obj.get_designation()
        return desig.name if desig else None
    
    def get_shift_name(self, obj):
        shift = obj.get_shift()
        return shift.name if shift else None


class EmployeePersonalInfoSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeePersonalInfo
        fields = '__all__'


class EmployeeEducationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeeEducation
        fields = '__all__'


class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeeSalary
        fields = '__all__'


class EmployeeSkillSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    
    class Meta:
        model = EmployeeSkill
        fields = '__all__'


# ==================== ATTENDANCE SERIALIZERS ====================

class AttendanceLogSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceLog
        fields = '__all__'
    
    def get_employee_name(self, obj):
        employee = obj.get_employee()
        return employee.get_full_name() if employee else None


class AttendanceLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for ZKTeco device push data"""
    class Meta:
        model = AttendanceLog
        fields = [
            'user_id', 'punch_time', 'status', 'verify_type', 
            'work_code', 'device_sn', 'raw_data'
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    shift_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = '__all__'
    
    def get_shift_name(self, obj):
        shift = obj.get_shift()
        return shift.name if shift else None


# ==================== LEAVE MANAGEMENT SERIALIZERS ====================

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    leave_type_name = serializers.SerializerMethodField()
    remaining_days = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaveBalance
        fields = '__all__'
    
    def get_leave_type_name(self, obj):
        leave_type = obj.get_leave_type()
        return leave_type.name if leave_type else None


class LeaveApplicationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    leave_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveApplication
        fields = '__all__'
    
    def get_leave_type_name(self, obj):
        leave_type = obj.get_leave_type()
        return leave_type.name if leave_type else None


# ==================== OTHER SERIALIZERS ====================

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'


class OvertimeSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    shift_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Overtime
        fields = '__all__'
    
    def get_shift_name(self, obj):
        shift = obj.get_shift()
        return shift.name if shift else None


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class UserLocationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = UserLocation
        fields = '__all__'


class RosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roster
        fields = '__all__'


class RosterAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    roster_name = serializers.CharField(source='roster.name', read_only=True)
    shift_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RosterAssignment
        fields = '__all__'
    
    def get_shift_name(self, obj):
        shift = obj.get_shift()
        return shift.name if shift else None


class RosterDaySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='user_id.get_full_name', read_only=True)
    shift_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RosterDay
        fields = '__all__'
    
    def get_shift_name(self, obj):
        shift = obj.get_shift()
        return shift.name if shift else None


# ==================== ZKTECO DEVICE PUSH SERIALIZERS ====================
class ZKTecoAttendanceSerializer(serializers.Serializer):
    """Serializer for ZKTeco device attendance push data (GET method)"""
    SN = serializers.CharField(max_length=100, help_text="Device Serial Number")
    ATTLOG = serializers.CharField(required=False, help_text="Attendance log data")
    
    def create(self, validated_data):
        """Process ZKTeco attendance data from GET"""
        sn = validated_data.get('SN', '')
        attlog = validated_data.get('ATTLOG', '')
        
        if attlog:
            parts = attlog.split(",")
            if len(parts) >= 2:
                user_id = parts[0]
                punch_time_str = parts[1]
                status = parts[2] if len(parts) > 2 else ""
                verify = parts[3] if len(parts) > 3 else ""
                workcode = parts[4] if len(parts) > 4 else ""
                
                punch_time = datetime.strptime(punch_time_str, "%Y-%m-%d %H:%M:%S")
                punch_time = timezone.make_aware(punch_time)
                
                return AttendanceLog.objects.create(
                    user_id=user_id,
                    punch_time=punch_time,
                    status=status,
                    verify_type=verify,
                    work_code=workcode,
                    device_sn=sn,
                    raw_data=str(validated_data)
                )
        return None


class ZKTecoPostDataSerializer(serializers.Serializer):
    """Serializer for ZKTeco device POST data (ATTLOG table)"""
    body_data = serializers.CharField(help_text="POST body data from device")
    device_sn = serializers.CharField(max_length=100, help_text="Device Serial Number")
    
    def create(self, validated_data):
        """Process ZKTeco POST attendance data"""
        body = validated_data.get('body_data', '')
        sn = validated_data.get('device_sn', '')
        
        created_logs = []
        if body:
            lines = body.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        user_id = parts[0]
                        punch_time_str = parts[1]
                        status = parts[2] if len(parts) > 2 else ""
                        verify = parts[3] if len(parts) > 3 else ""
                        workcode = parts[4] if len(parts) > 4 else ""
                        
                        try:
                            punch_time = datetime.strptime(punch_time_str, "%Y-%m-%d %H:%M:%S")
                            punch_time = timezone.make_aware(punch_time)
                            
                            log = AttendanceLog.objects.create(
                                user_id=user_id,
                                punch_time=punch_time,
                                status=status,
                                verify_type=verify,
                                work_code=workcode,
                                device_sn=sn,
                                raw_data=body
                            )
                            created_logs.append(log)
                        except Exception as e:
                            print(f"Error parsing attendance: {e}")
        
        return created_logs


class ZKTecoUserDataSerializer(serializers.Serializer):
    """Serializer for ZKTeco device USER table data"""
    body_data = serializers.CharField(help_text="POST body data with user info")
    device_sn = serializers.CharField(max_length=100, help_text="Device Serial Number")
    
    def create(self, validated_data):
        """Process ZKTeco USER data"""
        body = validated_data.get('body_data', '')
        sn = validated_data.get('device_sn', '')
        
        created_users = []
        updated_users = []
        
        if body:
            lines = body.strip().split('\n')
            
            for line in lines:
                if line.strip():
                    # Format: user_id\tname\tprivilege\tpassword\tcardno\tgroup
                    parts = line.strip().split('\t')
                    
                    if len(parts) >= 2:
                        user_id = parts[0].strip()
                        name = parts[1].strip() if len(parts) > 1 else ""
                        privilege = parts[2].strip() if len(parts) > 2 else ""
                        password = parts[3].strip() if len(parts) > 3 else ""
                        card_no = parts[4].strip() if len(parts) > 4 else ""
                        group = parts[5].strip() if len(parts) > 5 else ""
                        
                        # Split name into first_name and last_name
                        name_parts = name.split(' ', 1)
                        first_name = name_parts[0] if name_parts else user_id
                        last_name = name_parts[1] if len(name_parts) > 1 else ""
                        
                        try:
                            # Create or update employee
                            employee, created = Employee.objects.update_or_create(
                                user_id=user_id,
                                defaults={
                                    'employee_id': card_no or user_id,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'is_active': True
                                }
                            )
                            
                            if created:
                                created_users.append(employee)
                            else:
                                updated_users.append(employee)
                                
                        except Exception as e:
                            print(f"Error creating/updating user {user_id}: {e}")
        
        return {
            'created': created_users,
            'updated': updated_users,
            'device_sn': sn
        }