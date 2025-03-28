# -*- coding: utf-8 -*-

from . import controllers
from . import models

def post_init_hook(cr, registry):
    """Post init hook for ensuring dashboard exists"""
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['lms.dashboard']._ensure_dashboard_exists()
