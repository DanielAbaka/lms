# -*- coding: utf-8 -*-
{
    'name': 'Learning Management System',
    'version': '16.0.1.0.0',
    'category': 'Education',
    'summary': 'Comprehensive Learning Management System for Educational Institutions',
    'description': """
    Learning Management System
    =================================
    
    Key Features:
    ------------
    * Academic Year & Semester Management
    * Comprehensive Course Management
    * Course Material Management
    * Interactive Course Scheduling
    * Role-based Access Control
    * Professional Dashboard Interface
    
    This module provides a complete solution for educational institutions to manage their academic operations.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'web',
        'portal',
        'resource',
        'website',
    ],
    'data': [
        # Security
        'security/security_rules.xml',
        'security/ir.model.access.csv',
        
        # Views
        'views/menu_views.xml',
        'views/semester_views.xml',
        'views/course_views.xml',
        'views/course_material_views.xml',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'static/src/scss/styles.scss',
            'static/src/js/dashboard.js',
        ],
    },
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 1,
}





