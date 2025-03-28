# -*- coding: utf-8 -*-
{
    'name': 'Learning Management System',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Manage courses, students, and learning materials',
    'description': """
        Learning Management System for educational institutions.
        Features:
        - Course Management
        - Student Management
        - Teacher Management
        - Course Materials
        - Attendance Tracking
        - Grade Management
        - Quiz Management
        - Student and Teacher Portals
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'mail', 'portal', 'web', 'website_slides'],
    'data': [
        # Security
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/lms_security.xml",
        
        # First load all model views
        'views/views.xml',
        'views/course_views.xml',
        'views/quiz_views.xml',
        'views/quiz_question_views.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
        'views/attendance_views.xml',
        'views/academic_year_views.xml',
        'views/semester_views.xml',
        'views/course_material_views.xml',
        'views/course_planning_views.xml',
        'views/document_views.xml',
        'views/document_access_views.xml',
        'views/enrollment_views.xml',
        'views/grade_views.xml',
        'views/teacher_assignment_views.xml',
        'views/schedule_views.xml',
        'views/transcript_views.xml',
        'views/payment_views.xml',
        'views/payment_plan_views.xml',
        'views/administrator_views.xml',
        'views/bulk_enrollment_views.xml',
        
        # Actions must be loaded before menus
        'views/menu_actions.xml',
        
        # Menu last
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}





