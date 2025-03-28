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
        "security/models_data.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        
        # Core Views
        'views/views.xml',
        'views/menu.xml',
        'views/templates.xml',
        
        # Portal Views
        'views/student_portal_views.xml',
        'views/teacher_portal_views.xml',
        'views/admin_portal_views.xml',
        
        # Feature Views
        'views/quiz_views.xml',
        'views/quiz_question_views.xml',
        'views/quiz_option_views.xml',
        'views/quiz_attempt_views.xml',
        'views/quiz_question_attempt_views.xml',
        'views/course_views.xml',
        'views/messaging_views.xml',
    ],
    'demo': [
        'demo/lms_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}





