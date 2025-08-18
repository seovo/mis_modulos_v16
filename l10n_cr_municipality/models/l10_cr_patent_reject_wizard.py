from odoo import _, fields, models


class PatentDenyWizard(models.TransientModel):
    _name = "l10n_cr.patent.reject_wizard"
    _description = "CR Patent Reject Wizard"

    patent_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        required=True,
        default=lambda self: self.env["l10n_cr.patent"].browse(self._context["active_id"]),
        readonly=True,
    )
    
    reject_motive = fields.Text(
        string='Motivos'
    )
    

    def reject(self):
        for wizard in self:
            wizard.patent_id.reject_motive = self.reject_motive
            wizard.patent_id.state = "rejected"
            wizard.patent_id.resolution_date = fields.Date.today()
            display_msg = """La patente """ + wizard.patent_id.name + """,
               <br/>
               fue denegada por los siguientes motivos:
               <br/>
               """ + wizard.patent_id.reject_motive + """
               <br/>"""
            wizard.patent_id.message_post(body=display_msg)
        return {}
