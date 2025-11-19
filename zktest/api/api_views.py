from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import (
    Department, Designation, Shift, Employee, EmployeePersonalInfo,
    EmployeeEducation, EmployeeSalary, EmployeeSkill, AttendanceLog,
    Attendance, LeaveType, LeaveBalance, LeaveApplication, Holiday,
    Overtime, Notice, Location, UserLocation, Roster, RosterAssignment,
    RosterDay
)

from .serializers import (
    DepartmentSerializer, DesignationSerializer, ShiftSerializer,
    EmployeeSerializer, EmployeePersonalInfoSerializer, EmployeeEducationSerializer,
    EmployeeSalarySerializer, EmployeeSkillSerializer, AttendanceLogSerializer,
    AttendanceLogCreateSerializer, AttendanceSerializer, LeaveTypeSerializer,
    LeaveBalanceSerializer, LeaveApplicationSerializer, HolidaySerializer,
    OvertimeSerializer, NoticeSerializer, LocationSerializer,
    UserLocationSerializer, RosterSerializer, RosterAssignmentSerializer,
    RosterDaySerializer, ZKTecoAttendanceSerializer, ZKTecoPostDataSerializer
)


# ==================== BASIC MODELS VIEWSETS ====================

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'level']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'level', 'created_at']
    ordering = ['level', 'name']


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_night_shift']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'start_time', 'created_at']
    ordering = ['start_time']


# ==================== EMPLOYEE VIEWSETS ====================

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'employment_status', 'department_code', 'designation_code']
    search_fields = ['user_id', 'employee_id', 'first_name', 'last_name', 'email']
    ordering_fields = ['employee_id', 'first_name', 'joining_date', 'created_at']
    ordering = ['employee_id']


class EmployeePersonalInfoViewSet(viewsets.ModelViewSet):
    queryset = EmployeePersonalInfo.objects.all()
    serializer_class = EmployeePersonalInfoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['gender', 'marital_status', 'blood_group']
    search_fields = ['user_id__first_name', 'user_id__last_name', 'nid', 'passport_no']


class EmployeeEducationViewSet(viewsets.ModelViewSet):
    queryset = EmployeeEducation.objects.all()
    serializer_class = EmployeeEducationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['education_level', 'passing_year']
    search_fields = ['degree_title', 'institution', 'user_id__first_name']
    ordering_fields = ['passing_year', 'created_at']
    ordering = ['-passing_year']


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['user_id__first_name', 'user_id__last_name', 'bank_name']


class EmployeeSkillViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSkill.objects.all()
    serializer_class = EmployeeSkillSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['skill_level', 'years_of_experience']
    search_fields = ['skill_name', 'user_id__first_name', 'user_id__last_name']
    ordering_fields = ['skill_name', 'years_of_experience', 'created_at']
    ordering = ['skill_name']


# ==================== ATTENDANCE VIEWSETS ====================

class AttendanceLogViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLog.objects.all()
    serializer_class = AttendanceLogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'device_sn', 'status', 'is_processed']
    search_fields = ['user_id', 'device_sn']
    ordering_fields = ['punch_time', 'created_at']
    ordering = ['-punch_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return AttendanceLogCreateSerializer
        return AttendanceLogSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'date', 'status', 'shift_code']
    search_fields = ['user_id__first_name', 'user_id__last_name', 'user_id__employee_id']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']


# ==================== LEAVE MANAGEMENT VIEWSETS ====================

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_active', 'paid', 'requires_approval']
    search_fields = ['name', 'code']
    ordering = ['name']


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'leave_type_code', 'year']
    search_fields = ['user_id__first_name', 'user_id__last_name']
    ordering_fields = ['year', 'created_at']
    ordering = ['-year']


class LeaveApplicationViewSet(viewsets.ModelViewSet):
    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveApplicationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'leave_type_code', 'status', 'start_date']
    search_fields = ['user_id__first_name', 'user_id__last_name', 'reason']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']


# ==================== OTHER VIEWSETS ====================

class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_optional', 'date']
    search_fields = ['name', 'description']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']


class OvertimeViewSet(viewsets.ModelViewSet):
    queryset = Overtime.objects.all()
    serializer_class = OvertimeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'date', 'status', 'overtime_type']
    search_fields = ['user_id__first_name', 'user_id__last_name']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'priority', 'published_date']
    search_fields = ['title', 'description']
    ordering_fields = ['published_date', 'priority', 'created_at']
    ordering = ['-published_date']


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'address']
    ordering = ['name']


class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['user_id', 'location', 'is_primary']
    search_fields = ['user_id__first_name', 'user_id__last_name', 'location__name']


class RosterViewSet(viewsets.ModelViewSet):
    queryset = Roster.objects.all()
    serializer_class = RosterSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']


class RosterAssignmentViewSet(viewsets.ModelViewSet):
    queryset = RosterAssignment.objects.all()
    serializer_class = RosterAssignmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['roster', 'user_id', 'shift_code']
    search_fields = ['user_id__first_name', 'user_id__last_name', 'roster__name']


class RosterDayViewSet(viewsets.ModelViewSet):
    queryset = RosterDay.objects.all()
    serializer_class = RosterDaySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'date', 'shift_code', 'is_off']
    search_fields = ['user_id__first_name', 'user_id__last_name']
    ordering_fields = ['date', 'created_at']
    ordering = ['date']


# ==================== ZKTECO DEVICE PUSH API VIEWS ====================

@method_decorator(csrf_exempt, name='dispatch')
class ZKTecoAttendancePushView(APIView):
    """
    ZKTeco device attendance push endpoint
    Handles both GET and POST requests from ZKTeco devices
    
    Endpoints:
    - /iclock/getrequest (GET) - ZKTeco device push protocol
    - /iclock/cdata (POST) - ZKTeco device bulk data protocol
    - /zk-push/ (GET) - Alternative endpoint
    - /zk-cdata/ (POST) - Alternative endpoint
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Handle GET request from ZKTeco device"""
        sn = request.GET.get('SN', '')
        attlog = request.GET.get('ATTLOG', '')
        
        if attlog:
            serializer = ZKTecoAttendanceSerializer(data={
                'SN': sn,
                'ATTLOG': attlog
            })
            
            if serializer.is_valid():
                attendance_log = serializer.save()
                if attendance_log:
                    return HttpResponse("OK")
                else:
                    return HttpResponse("ERROR: Failed to create attendance log", status=400)
            else:
                return HttpResponse(f"ERROR: {serializer.errors}", status=400)
        
        return HttpResponse("OK")
    
    def post(self, request):
        """Handle POST request from ZKTeco device"""
        sn = request.GET.get('SN', '')
        table = request.GET.get('table', '')
        
        # Get the POST body data
        body = request.body.decode('utf-8', errors='ignore')
        
        if table == 'ATTLOG' and body:
            serializer = ZKTecoPostDataSerializer(data={
                'body_data': body,
                'device_sn': sn
            })
            
            if serializer.is_valid():
                created_logs = serializer.save()
                return HttpResponse("OK")
            else:
                return HttpResponse(f"ERROR: {serializer.errors}", status=400)
        
        return HttpResponse("OK")


# ==================== CUSTOM API VIEWS ====================

@api_view(['GET'])
def employee_attendance_summary(request, user_id):
    """Get attendance summary for a specific employee"""
    try:
        employee = Employee.objects.get(user_id=user_id)
        attendances = Attendance.objects.filter(user_id=employee).order_by('-date')[:30]
        
        serializer = AttendanceSerializer(attendances, many=True)
        return Response({
            'employee': EmployeeSerializer(employee).data,
            'recent_attendances': serializer.data
        })
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)


@api_view(['GET'])
def attendance_logs_by_device(request, device_sn):
    """Get attendance logs for a specific device"""
    logs = AttendanceLog.objects.filter(device_sn=device_sn).order_by('-punch_time')[:100]
    serializer = AttendanceLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def process_attendance_logs(request):
    """Process unprocessed attendance logs into daily attendance records"""
    unprocessed_logs = AttendanceLog.objects.filter(is_processed=False)
    processed_count = 0
    
    # Group logs by user_id and date
    from collections import defaultdict
    grouped_logs = defaultdict(list)
    
    for log in unprocessed_logs:
        date_key = f"{log.user_id}_{log.punch_time.date()}"
        grouped_logs[date_key].append(log)
    
    # Process each group
    for date_key, logs in grouped_logs.items():
        user_id, date_str = date_key.split('_', 1)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        try:
            employee = Employee.objects.get(user_id=user_id)
            
            # Get or create attendance record
            attendance, created = Attendance.objects.get_or_create(
                user_id=employee,
                date=date,
                defaults={
                    'status': 'present',
                    'shift_code': employee.shift_code or '',
                }
            )
            
            # Update check-in and check-out times
            logs.sort(key=lambda x: x.punch_time)
            if logs:
                attendance.check_in_time = logs[0].punch_time
                if len(logs) > 1:
                    attendance.check_out_time = logs[-1].punch_time
                
                # Calculate work hours (basic calculation)
                if attendance.check_in_time and attendance.check_out_time:
                    work_duration = attendance.check_out_time - attendance.check_in_time
                    attendance.work_hours = work_duration.total_seconds() / 3600
                
                attendance.processed_from_logs = True
                attendance.last_processed_at = datetime.now()
                attendance.save()
            
            # Mark logs as processed
            for log in logs:
                log.is_processed = True
                log.processed_at = datetime.now()
                log.save()
            
            processed_count += 1
            
        except Employee.DoesNotExist:
            continue
    
    return Response({
        'message': f'Processed {processed_count} attendance records',
        'processed_logs': len(unprocessed_logs)
    })


@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics"""
    from django.db.models import Count
    from datetime import date, timedelta
    
    today = date.today()
    
    stats = {
        'total_employees': Employee.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_shifts': Shift.objects.filter(is_active=True).count(),
        'today_attendance': Attendance.objects.filter(date=today).count(),
        'today_present': Attendance.objects.filter(date=today, status='present').count(),
        'today_absent': Attendance.objects.filter(date=today, status='absent').count(),
        'pending_leaves': LeaveApplication.objects.filter(status='pending').count(),
        'unprocessed_logs': AttendanceLog.objects.filter(is_processed=False).count(),
    }
    
    return Response(stats)