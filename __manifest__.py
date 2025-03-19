# -*- coding: utf-8 -*-
{
    'name': "LMS Module",

    'summary': "A Learning Management System for managing courses, students, teachers, enrollments, and more.",

    'description': """
Long description of module's purpose
    """,

    'author': "CS4LIBERIA",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_slides','survey','hr','payment','mail'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',

        # 'security/lms_security.xml',
        'views/views.xml',
        'views/menu.xml',
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



    ],
    # only loaded in demonstration mode
    'installable': True,
    'application': True,
    'auto_install': False,
}





