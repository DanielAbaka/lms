from odoo import models, fields, api

class StudentProfile(models.Model):
    _inherit = 'res.users'

    is_student = fields.Boolean(string="Is Student", default=False)
    student_id = fields.Char(string="Student ID", required=True, unique=True)
    enrolled_courses = fields.Many2many(
        'slide.channel',
        'lms_student_course_rel',
        'student_id',
        'course_id',
        string="Enrolled Courses"
    )
    dashboard_data = fields.Text(string="Dashboard Data", compute="_compute_dashboard_data")

    # Personal Information
    firstname = fields.Char(string="First Name", required=True)
    lastname = fields.Char(string="Last Name", required=True)
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender")
    address = fields.Text(string="Address")
    phone = fields.Char(string="Phone")
    emergency_contact = fields.Char(string="Emergency Contact")
    
    # Academic Information
    major = fields.Char(string="Major")
    minor = fields.Char(string="Minor")
    
    # Academic Progress
    gpa = fields.Float(string="GPA", digits=(3, 2))
    academic_status = fields.Selection([
        ('good_standing', 'Good Standing'),
        ('probation', 'Academic Probation'),
        ('suspended', 'Suspended')
    ], string="Academic Status", default='good_standing')

    @api.depends('enrolled_courses')
    def _compute_dashboard_data(self):
        for record in self:
            enrolled_courses = record.enrolled_courses.mapped('name')
            record.dashboard_data = f"Enrolled Courses: {', '.join(enrolled_courses)}"

    @api.model
    def create(self, vals):
        """When creating a user with is_student=True, add them to the student group."""
        if vals.get('is_student'):
            student_group = self.env.ref('lms_module.group_lms_student', raise_if_not_found=False)
            if student_group:
                # Add the user to the student group
                # If there's an existing groups_id, we append (4, group_id)
                existing_groups = vals.get('groups_id', [])
                vals['groups_id'] = existing_groups + [(4, student_group.id)]
        return super().create(vals)