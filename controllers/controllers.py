# File: lms_module/controllers.py

import json
from odoo import http
from odoo.http import request, Response


class LMSController(http.Controller):
    # =================================================================
    # STUDENTS (res.users with is_student=True)
    # =================================================================
    @http.route('/lms/students', auth='public', methods=['GET'], type='json', csrf=False)
    def get_students(self):
        """Return all users with is_student=True."""
        Student = request.env['res.users'].sudo()
        students = Student.search([('is_student', '=', True)])
        return [self._student_to_dict(stu) for stu in students]

    @http.route('/lms/students/<int:student_id>', auth='public', methods=['GET'], type='json', csrf=False)
    def get_student_by_id(self, student_id):
        """Return a single student by ID, if is_student=True."""
        stu = request.env['res.users'].sudo().search([
            ('id', '=', student_id),
            ('is_student', '=', True)
        ], limit=1)
        if not stu:
            return {'error': 'Student not found'}
        return self._student_to_dict(stu)

    @http.route('/lms/students/create', auth='public', methods=['POST'], type='json', csrf=False)
    def create_student(self, **post):
        """Create a new student user record, forcing is_student=True."""
        vals = {
            'name': post.get('name'),
            'student_id': post.get('student_id'),
            'is_student': True,  # ensures they're recognized as a student
        }
        new_student = request.env['res.users'].sudo().create(vals)
        return self._student_to_dict(new_student)

    def _student_to_dict(self, stu):
        return {
            'id': stu.id,
            'name': stu.name,
            'student_id': stu.student_id,
            'is_student': stu.is_student,
        }

    # =================================================================
    # TEACHERS (res.users with is_teacher=True)
    # =================================================================
    @http.route('/lms/teachers', auth='public', methods=['GET'], type='json', csrf=False)
    def get_teachers(self):
        """Return all users with is_teacher=True."""
        Teacher = request.env['res.users'].sudo()
        teachers = Teacher.search([('is_teacher', '=', True)])
        return [self._teacher_to_dict(t) for t in teachers]

    @http.route('/lms/teachers/<int:teacher_id>', auth='public', methods=['GET'], type='json', csrf=False)
    def get_teacher_by_id(self, teacher_id):
        """Return a single teacher by ID, if is_teacher=True."""
        teacher = request.env['res.users'].sudo().search([
            ('id', '=', teacher_id),
            ('is_teacher', '=', True)
        ], limit=1)
        if not teacher:
            return {'error': 'Teacher not found'}
        return self._teacher_to_dict(teacher)

    @http.route('/lms/teachers/create', auth='public', methods=['POST'], type='json', csrf=False)
    def create_teacher(self, **post):
        """Create a new teacher user record, forcing is_teacher=True."""
        vals = {
            'name': post.get('name'),
            'is_teacher': True,
        }
        new_teacher = request.env['res.users'].sudo().create(vals)
        return self._teacher_to_dict(new_teacher)

    def _teacher_to_dict(self, t):
        return {
            'id': t.id,
            'name': t.name,
            'email': t.email,
            'is_teacher': t.is_teacher,
        }

    # =================================================================
    # COURSES (slide.channel)
    # =================================================================
    @http.route('/lms/courses', auth='public', methods=['GET'], type='json', csrf=False)
    def get_courses(self):
        Course = request.env['slide.channel'].sudo()
        courses = Course.search([])
        return [self._course_to_dict(c) for c in courses]

    def _course_to_dict(self, c):
        return {
            'id': c.id,
            'name': c.name,
            'credits': c.credits,
            'cost_per_credit': getattr(c, 'cost_per_credit', 0.0),
        }

    # =================================================================
    # GRADES (lms.grade)
    # =================================================================
    @http.route('/lms/grades', auth='public', methods=['GET'], type='json', csrf=False)
    def get_grades(self):
        Grade = request.env['lms.grade'].sudo()
        grades = Grade.search([])
        return [self._grade_to_dict(g) for g in grades]

    def _grade_to_dict(self, g):
        return {
            'id': g.id,
            'student_id': g.student_id.id,
            'course_id': g.course_id.id,
            'grade': g.grade,
            'remarks': g.remarks,
        }

    # =================================================================
    # ENROLLMENTS (lms.enrollment)
    # =================================================================
    @http.route('/lms/enrollments', auth='public', methods=['GET'], type='json', csrf=False)
    def get_enrollments(self):
        Enroll = request.env['lms.enrollment'].sudo()
        enrolls = Enroll.search([])
        return [self._enrollment_to_dict(e) for e in enrolls]

    def _enrollment_to_dict(self, e):
        return {
            'id': e.id,
            'student_id': e.student_id.id,
            'course_ids': [c.id for c in e.course_id],
            'enrollment_date': e.enrollment_date,
            'payment_status': e.payment_status,
            'total_cost': e.total_cost,
            'remaining_balance': e.remaining_balance,
        }

    # =================================================================
    # COURSE PLANNING (lms.course.planning)
    # =================================================================
    @http.route('/lms/course_planning', auth='public', methods=['GET'], type='json', csrf=False)
    def get_course_planning(self):
        Plan = request.env['lms.course.planning'].sudo()
        plans = Plan.search([])
        return [self._plan_to_dict(p) for p in plans]

    def _plan_to_dict(self, p):
        return {
            'id': p.id,
            'student_id': p.student_id.id,
            'semester_id': p.semester_id.id,
            'course_ids': [c.id for c in p.course_ids],
            'total_credits': p.total_credits,
            'total_cost': p.total_cost,
            'is_enrolled': p.is_enrolled,
        }

    # =================================================================
    # TRANSCRIPTS (lms.transcript)
    # =================================================================
    @http.route('/lms/transcripts', auth='public', methods=['GET'], type='json', csrf=False)
    def get_transcripts(self):
        Trans = request.env['lms.transcript'].sudo()
        transcripts = Trans.search([])
        return [self._transcript_to_dict(t) for t in transcripts]

    def _transcript_to_dict(self, t):
        return {
            'id': t.id,
            'student_id': t.student_id.id,
            'academic_year_id': t.academic_year_id.id if t.academic_year_id else False,
            'semester_id': t.semester_id.id if t.semester_id else False,
            'course_ids': [c.id for c in t.course_ids],
            'total_credits': t.total_credits,
            'gpa': t.gpa,
        }

    # =================================================================
    # DOCUMENTS (custom model lms.document or binary approach)
    # =================================================================
    @http.route('/lms/documents', auth='public', methods=['GET'], type='json', csrf=False)
    def get_documents(self):
        Doc = request.env['lms.document'].sudo()
        docs = Doc.search([])
        return [self._doc_to_dict(d) for d in docs]

    def _doc_to_dict(self, d):
        return {
            'id': d.id,
            'name': d.name,
            'course_id': d.course_id.id if d.course_id else False,
            # If using binary field or attachment reference, we won't return the file inline
        }

    # =================================================================
    # PAYMENTS (inherit from payment.transaction or custom model)
    # =================================================================
    @http.route('/lms/payments', auth='public', methods=['GET'], type='json', csrf=False)
    def get_payments(self):
        Payment = request.env['payment.transaction'].sudo()  # Or your custom model if used
        pay_records = Payment.search([])
        return [self._payment_to_dict(p) for p in pay_records]

    def _payment_to_dict(self, p):
        return {
            'id': p.id,
            'reference': p.reference,
            'amount': p.amount,
            'state': p.state,
            # if you have a custom enrollment_id: 'enrollment_id': p.enrollment_id.id
        }

    # =================================================================
    # MESSAGING (lms.messaging)
    # =================================================================
    @http.route('/lms/messages', auth='public', methods=['GET'], type='json', csrf=False)
    def get_messages(self):
        Msg = request.env['lms.messaging'].sudo()
        msgs = Msg.search([])
        return [self._msg_to_dict(m) for m in msgs]

    def _msg_to_dict(self, m):
        return {
            'id': m.id,
            'message_content': m.message_content,
            'sender_id': m.sender_id.id if m.sender_id else False,
            'recipient_ids': [r.id for r in m.recipient_ids],
        }

    # =================================================================
    # TEACHER ASSIGNMENTS (lms.teacher.assignment)
    # =================================================================
    @http.route('/lms/teacher_assignments', auth='public', methods=['GET'], type='json', csrf=False)
    def get_teacher_assignments(self):
        TA = request.env['lms.teacher.assignment'].sudo()
        tas = TA.search([])
        return [self._ta_to_dict(t) for t in tas]

    def _ta_to_dict(self, t):
        return {
            'id': t.id,
            'teacher_id': t.teacher_id.id,
            'course_id': t.course_id.id,
            'start_date': t.start_date,
            'end_date': t.end_date,
        }

    # =================================================================
    #  Helper Payment Parser
    # =================================================================
    def _payment_to_dict(self, p):
        """See above."""

    # =================================================================
    #  OTHER CRUD endpoints (create, update, delete) as needed
    # =================================================================
    # e.g. /lms/courses/create (POST) → self.env['slide.channel'].sudo().create(vals)
    # or /lms/teacher_assignments/<id>/delete (DELETE)...