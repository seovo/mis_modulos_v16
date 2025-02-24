from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    def print_report_clinicos(self):
        return self.env.ref('report_project_clinicosas_jz.action_report_project').report_action(self)

