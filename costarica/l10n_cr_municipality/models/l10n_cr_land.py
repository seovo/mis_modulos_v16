from odoo import api, fields, models


class Land(models.Model):
    _inherit = "mail.thread"
    _name = "l10n_cr.land"
    _description = "CR Land"

    name = fields.Char(
        compute="_compute_name",
        store=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id.id
    )
    county_id = fields.Many2one(
        related="company_id.county_id",
    )
    land_type = fields.Selection(
        selection=[
            ("real_folio", "Real Folio"),
            ("plan_number", "Plan Number"),
            ("no_real_folio", "No Real Folio"),
        ],
        required=True, string=u'Tipo de propiedad'
    )
    land_number = fields.Char(
        required=True, string=u'Número de propiedad'
    )
    duplicate = fields.Char(string=u'Duplicado')
    horizontal = fields.Char(string=u'Horizontal')
    tome = fields.Char(string=u'Tomo')
    folio = fields.Char(string=u'Folio')
    seat = fields.Char(string=u'Sede')
    rights_qty = fields.Integer(
        string="Nº de Derechos",
    )
    plan_number = fields.Char(
        string="Nº de Plano",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("taxpayer", "=", True)],
    )

    address = fields.Char(
        string="Dirección",
    )
    district_id = fields.Many2one(
        comodel_name="res.country.district",
        # TODO domain=[]
    )
    zone = fields.Selection(
        selection=[
            ("rural", "Rural"),
            ("insdustrial", "Industrial"),
            ("other", "Other"),
        ],
    )
    gis = fields.Char()

    area = fields.Float()
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        # TODO domain=[]
    )
    allotment_type = fields.Selection(
        selection=[
            ("registered", "Registered"),
            ("no_registered", "No Registered"),
            ("possessory", "Possessory"),
            ("other", "Other"),
        ]
    )

    land = fields.Float()
    constructions = fields.Float()
    total_value = fields.Float()
    last_declaration_date = fields.Date()

    @api.depends("land_type", "land_number")
    def _compute_name(self):
        for land in self:
            translations = {
                "real_folio": "Folio Real",
                "plan_number": "Nº de Plano",
                "no_real_folio": "Sin Folio Real",
            }
            land.name = f"{translations.get(land.land_type, 'NA')}-{land.land_number}"
