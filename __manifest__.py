# -*- coding: utf-8 -*-
{
    'name': "LMS Module",

    'summary': "A Learning Management System for managing courses, students, teachers, enrollments, and more.",

    'description': """
Modern Learning Management System with a professional BlackBoard-inspired UI/UX. 
Features include course management, student enrollment, teacher assignments, grades, and more.
    """,

    'author': "CS4LIBERIA",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Education',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_slides', 'survey', 'hr', 'payment', 'mail', 'web'],

    # always loaded
    'data': [
        # Security
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/lms_security.xml',
        
        # Assets
        'static/src/lms_assets.xml',
        
        # Views
        'views/views.xml',
        'views/menu.xml',
        'views/dashboard_views.xml',
        'views/student_views.xml',
        'views/course_views.xml',
        'views/course_planning_views.xml',
        'views/enrollment_views.xml',
        'views/academic_year_views.xml',
        'views/semester_views.xml',
        'views/teacher_views.xml',
        'views/teacher_assignment_views.xml',
        'views/grade_views.xml',
        'views/payment_views.xml',
        'views/transcript_views.xml',
        'views/document_views.xml',
        'views/messaging_views.xml',
        'views/templates.xml',
    ],
    
    'assets': {
        'web.assets_backend': [
            'lms/static/src/scss/lms_style.scss',
        ],
    },
    
    # only loaded in demonstration mode
    'installable': True,
    'application': True,
    'auto_install': False,
}





