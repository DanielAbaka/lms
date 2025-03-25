# -*- coding: utf-8 -*-
{
    'name': 'Learning Management System',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Manage educational courses, students, and teachers',
    'description': """
        Learning Management System for educational institutions.
        Features:
        - Course Management
        - Student Management
        - Teacher Management
        - Enrollment Management
        - Attendance Tracking
        - Grade Management
        - Quiz System
        - Document Management
        - Payment Processing
        - Academic Year & Semester Management
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail', 'web', 'website_slides'],
    'data': [
        # Security
        'security/lms_security.xml',
        'security/ir.model.access.csv',
        
        # Core Views
        'views/views.xml',
        'views/templates.xml',
        'views/menu.xml',
        
        # Academic Management
        'views/academic_year_views.xml',
        'views/semester_views.xml',
        'views/course_views.xml',
        
        # Student Management
        'views/student_views.xml',
        'views/enrollment_views.xml',
        'views/course_planning_views.xml',
        'views/student_portal_views.xml',
        
        # Teaching Management
        'views/teacher_views.xml',
        'views/teacher_assignment_views.xml',
        'views/teacher_portal_views.xml',
        'views/course_material_views.xml',
        
        # Assessment
        'views/attendance_views.xml',
        'views/grade_views.xml',
        'views/transcript_views.xml',
        
        # Quiz System
        'views/quiz_views.xml',
        'views/quiz_question_views.xml',
        'views/quiz_option_views.xml',
        'views/quiz_attempt_views.xml',
        'views/quiz_question_attempt_views.xml',
        
        # Financial Management
        'views/payment_views.xml',
        'views/document_views.xml',
        'views/document_access_views.xml',
        
        # Communication
        'views/messaging_views.xml',
        
        # Administration
        'views/administrator_views.xml',
        'views/admin_portal_views.xml',
        'views/enhanced_views.xml',
        'views/schedule_views.xml',
    ],
    'demo': [
        'demo/lms_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}





