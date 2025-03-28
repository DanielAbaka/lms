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
        # Removed quiz related views that were causing issues
        'views/messaging_views.xml',
        
        # Portal views next
        'views/student_portal_views.xml',
        'views/teacher_portal_views.xml',
        'views/admin_portal_views.xml',
        
        # Actions must be loaded before menus
        'views/menu_actions.xml',
        
        # Menu last
        'views/menu.xml',
        'views/templates.xml',
        
        'views/enhanced_views.xml',
    ],
    'demo': [
        'demo/lms_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}





