# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError,ValidationError
import calendar

TYPE = [
    ('10','Prevención 1'),
    ('5','Prevención 2')
]

trimester_to_paid = {
    "t1": 3,
    "t2": 6,
    "t3": 9,
    "t4": 12,
}

month_to_trimester = {
    "1": "t1",
    "2": "t1",
    "3": "t1",
    "4": "t2",
    "5": "t2",
    "6": "t2",
    "7": "t3",
    "8": "t3",
    "9": "t3",
    "10": "t4",
    "11": "t4",
    "12": "t4",
}


CATEG = {
    "A": "A",
    "B1": "B1",
    "B2": "B2",
    "C": "C",
    "D1": "D1",
    "D2": "D2",
    "E1A": "E1A",
    "E1B": "E1B",
    "E2": "E2",
    "E3": "E3",
    "E4": "E4",
    "E5": "E5"
}
CONDITION = [
    ('normal','Normal'),
    ('cobro_1','Cobro 1'),
    ('cobro_2','Cobro 2'),
]


PERIOD = [
    ('2021','2021'),
    ('2022','2022'),
    ('2023','2023'),
    ('2024','2024'),
    ('2025','2025'),
]

class Patent(models.Model):
    _inherit = "mail.thread"
    _name = "l10n_cr.patent"
    _description = "CR Patent"

    name = fields.Char(
        default="Solicitud",
        readonly=True,
        string=u"Número",
        # TODO unique
        copy=False, tracking=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id.id, string=u'Compañia'
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        default=lambda self: self.env.user, string='Usuario'
    )

    currency_id = fields.Many2one(
        related="company_id.currency_id", string='Moneda'
    )
    county_id = fields.Many2one(
        related="company_id.county_id",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("taxpayer", "=", True)],
        required=True,string='Contribuyente'
    )
    vat = fields.Char(related='partner_id.vat',string=u'Documento de Identidad')

    solicitation_date = fields.Date(
        default=fields.Date.today, string='Fecha de solicitud'
    )
    type_id = fields.Many2one(
        required=True,
        comodel_name="l10n_cr.patent.type", string='Tipo'
    )
    type_code = fields.Char(
        related="type_id.code",
    )
    fantasy_name = fields.Char()
    needs_liqueur = fields.Boolean(
        string="Requiere Patente Licor",
    )
    is_liqueur = fields.Boolean(
        compute="_compute_is_liqueur",
    )
    activity_ids = fields.Many2many(
        comodel_name="l10n_cr.ciiu",string='Actividad'
    )
    commercial_activity = fields.Char(string='Actividad comercial')
    state = fields.Selection(
        string="Estado",
        selection=[
            ("requested", "Solicitada"),
            ('prevention', u'Prevenida'),
            ("in_progress", "En Proceso"),
            ("approved", "Aprobada"),
            ("rejected", "Rechazada"),
            ("suspended", "Suspendida"),
            ("retired", "Retirada"),
            ("canceled", "Cancelada"),
        ],
        default="requested",
        required=True,
        tracking=True,
        copy=False,
    )
    land_id = fields.Many2one(comodel_name="l10n_cr.land", string='Propiedad',required=False)
    address = fields.Char(
        related="land_id.address", string=u'Dirección'
    )
    district_id = fields.Many2one(
        related="land_id.district_id",
        readonly=False, string='Distrito', store=True
    )
    plan_number = fields.Char(
        related="land_id.plan_number",
        string=u'Número de plano'
    )
    relation_type = fields.Selection(
        selection=[
            ("rented", "Rented"),
            ("loaned", "Loaned"),
            ("owned", "Owned"),
        ],string=u'Tipo de relación'
    )
    area = fields.Float(string=u'Área')
    land_use_number = fields.Char(string='Uso de suelo')
    sanitary_permit = fields.Char(string='Permiso sanitario')
    sanitary_permit_expiration = fields.Date(string=u'Expiración permiso sanitario')
    comply_7600 = fields.Boolean(string='Cumple ley 7600 ?')
    income_total = fields.Monetary(
        string="Ingresos brutos",
    )
    yearly_payment = fields.Monetary(
        string="Pago Anual",
        compute="_compute_yearly_payment",
        store=True,
        readonly=False,
    )
    trimester_payment = fields.Monetary(
        string="Pago trimestral",
        compute="_compute_trimester_payment",
        inverse="_set_yearly_payment",
    )
    regimen = fields.Selection(
        string="Régimen",
        selection=[
            ("simplified", "Simplificado"),
            ("traditional", "Tradicional"),
        ],
    )
    category = fields.Selection(
        string=u"Categorías",
        selection=[
            ("commercial", "Comercial"),
            ("industrial", "Industrial"),
            ("services", "Servicios"),
            ("tourism", "Turismo"),
            ("agricultural", "Agropecuario"),
            ("entertainment", "Entretenimiento"),
            ("distribution", "Distribución"),
            ("financial", "Financiera"),
        ],
    )

    employees = fields.Integer(
        string="Cantidad de Empleados",
    )
    actives_value = fields.Monetary(
        string="Valor de los activos",
    )
    sales_value = fields.Monetary(
        string="Valor Ventas Netas",
    )
    score = fields.Float(
        string="Puntaje",
        compute="_compute_score",
    )
    category_liqueur = fields.Selection(
        string="Categoría",
        selection=[
            ("A", "Licorera (A)"),
            ("B1", "Bar (B1)"),
            ("B2", "Bar c/ actividad bailable (B2)"),
            ("C", "Restaurant (C)"),
            ("D1", "Minisúoer (D1)"),
            ("D2", "Supermercado (D2)"),
            ("E1A", "Hospedaje <15 (E1A)"),
            ("E1B", "Hospedaje >15 (E1B)"),
            ("E2", "Marinas (E2)"),
            ("E3", "Gastronómicas (E3)"),
            ("E4", "Centros nocturnos (E4)"),
            ("E5", "Actividades temáticas (E5)"),
        ],
    )
    subcategory_liqueur = fields.Selection(
        string="Subcategoría",
        selection=[
            ("A1", "A1"),
            ("A2", "A2"),
            ("A3", "A3"),
            ("A4", "A4"),
        ],
    )

    liqueur_patent_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        string="Patente de licor",
        readonly=True,
    )
    employees_rel = fields.Integer(
        related="liqueur_patent_id.employees",
        readonly=False,
    )
    actives_value_rel = fields.Monetary(
        related="liqueur_patent_id.actives_value",
        readonly=False,
    )
    sales_value_rel = fields.Monetary(
        related="liqueur_patent_id.sales_value",
        readonly=False,
    )
    yearly_payment_rel = fields.Monetary(
        # related="liqueur_patent_id.yearly_payment",
        compute="_compute_yearly_payment_rel",
        store=True,
    )
    trimester_payment_rel = fields.Monetary(
        string="Pago trimestral",
    )
    category_liqueur_rel = fields.Selection(
        related="liqueur_patent_id.category_liqueur",
        readonly=False,
    )
    subcategory_liqueur_rel = fields.Selection(
        related="liqueur_patent_id.subcategory_liqueur",
        readonly=False,
    )

    timbre = fields.Monetary(
        compute="_compute_timbre", string='Timbre'
    )
    yearly_payment_subtotal = fields.Monetary(
        string="Pago Anual",
        compute="_compute_payment_total",
    )
    yearly_payment_total = fields.Monetary(
        string="Pago Anual con Timbre",
        compute="_compute_payment_total",
    )
    trimester_payment_total = fields.Monetary(
        string="Pago Trimestral",
        compute="_compute_trimester_payment",
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        readonly=True,
    )

    liqueur_open_hour = fields.Float(
        string="Hora de Apertura",
        compute="_compute_liqueur_open_hour",
        store=True,
        readonly=False,
    )

    liqueur_close_hour = fields.Float(
        string="Hora de Cierre",
        compute="_compute_liqueur_close_hour",
        store=True,
        readonly=False,
    )
    liqueur_open_hour_rel = fields.Float(
        related="liqueur_patent_id.liqueur_open_hour",
        readonly=False,
    )

    liqueur_close_hour_rel = fields.Float(
        related="liqueur_patent_id.liqueur_close_hour",
        readonly=False,
    )
    req_deliver_id = fields.Many2many(
        "l10n_cr.req_deliver",
        column1="patent_id",
        column2="req_deliver_id",
        string="Requisitos de entrega",
    )
    req_miss_id = fields.Many2many(
        "l10n_cr.req_miss",
        column1="patent_id",
        column2="req_miss_id",
        string="Requisitos faltantes",
    )
    reject_motive = fields.Text(
        string="Motivo rechazo",
    )
    resolution_date = fields.Date(string=u"Fecha de resolución")
    property_owner = fields.Char(
        related="land_id.partner_id.name",
        string="Popietario",
        readonly=True,
    )
    pay_to = fields.Date(
        string="Pagado hasta el",
        readonly=True,
    )
    patent_origin_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        readonly=True,
    )

    number_resolution = fields.Char(string="Número de resolución", copy=False, store=True,  tracking=True)

    amount_prorate = fields.Monetary(string='Monto prorrateado')

    code_letter = fields.Char('letter')


    date_approved = fields.Date(string='Fecha de aprobación', copy=False, store=True,  tracking=True)

    number_preventive = fields.Char(store=True, copy=False, tracking=True)
    aprobado_por = fields.Many2one('hr.employee', string='Aprobador por: ', required=True)
    autorizado_por = fields.Many2one('hr.employee', string='Autorizado por: ', required=True)

    prevention_type = fields.Selection(TYPE, string='Escoja el tipo de prevención',default='10')

    condition = fields.Selection(CONDITION, string=u'Condición', default='normal')

    user_approved = fields.Many2one('hr.employee', string='Lo aprobo', compute='_compute_user_approved', store=True)

    is_web = fields.Boolean(string='Proviene de Web')
    change_name = fields.Boolean()

    #Campos sobreescritos en el módulo extendido
    year = fields.Integer()
    period = fields.Selection(PERIOD)
    generate_inv = fields.Boolean()

    @api.depends('state')
    def _compute_user_approved(self):
        for record in self:
            if record.state == 'approved':
                record.user_approved = record.write_uid.employee_id
            else:
                record.user_approved = False

    def create_liqueur_patent(self):
        self.liqueur_patent_id = self.copy(
            {
                "name": _("New"),
                "type_id": self.env.ref("l10n_cr_municipality.patent_type_liquors").id,
                "needs_liqueur": False,
                "employees": self.employees_rel,
                "actives_value": self.actives_value_rel,
                "sales_value": self.sales_value_rel,
                "yearly_payment": self.yearly_payment_rel,
                "patent_origin_id": self.id,
            }
        )

    def write(self, vals):
        res = super(Patent, self).write(vals)
        if vals.get("needs_liqueur"):
            self.create_liqueur_patent()
        if not self.condition:
            self.condition = 'normal'
        return res

    @api.model
    def create(self, vals):
        res = super(Patent, self).create(vals)

        patent_type = res.type_id
        sequence = patent_type.sequence_id
        district = res.land_id.district_id
        res.name = (
            f"{patent_type.code}-{district.code}-{sequence.sudo().next_by_id()}"  # TODO district.code
        )
        if res.needs_liqueur:
            res.create_liqueur_patent()

        if not self.condition:
            self.condition = 'normal'

        return res

    def get_payment_simplified(self):
        base_salary = float(self.env["ir.config_parameter"].sudo().get_param("l10n_cr.base_salary"))
        scales = [
            (0, 13 / 100 * base_salary),
            (25000000, 20 / 100 * base_salary),
            (50000000, 25 / 100 * base_salary),
            (65000000, 30 / 100 * base_salary),
        ]
        payment = 0
        for scale in scales:
            if self.income_total < scale[0]:
                break
            payment = scale[1]
        return payment

    @api.depends("regimen", "income_total")
    def _compute_yearly_payment(self):
        for patent in self:
            if patent.regimen == "traditional":
                patent.yearly_payment = patent.income_total * (1.5 / 1000)
            elif patent.regimen == "simplified":
                patent.yearly_payment = self.get_payment_simplified()
            else:
                patent.yearly_payment = 0
            if patent.type_id.code == "EM":
                base_salary = float(
                    self.env["ir.config_parameter"].sudo().get_param("l10n_cr.base_salary")
                )
                patent.yearly_payment = (10 / 100) * base_salary

    @api.depends("yearly_payment", "yearly_payment_total")
    def _compute_trimester_payment(self):
        for patent in self:
            patent.trimester_payment = patent.yearly_payment / 4
            patent.trimester_payment_total = patent.yearly_payment_total / 4

    @api.depends(
        "employees",
        "actives_value",
        "sales_value",
        "employees_rel",
        "actives_value_rel",
        "sales_value_rel",
    )
    def _compute_score(self):
        ntcs = float(self.env["ir.config_parameter"].sudo().get_param("l10n_cr.ntcs"))
        vncs = float(self.env["ir.config_parameter"].sudo().get_param("l10n_cr.vncs"))
        atcs = float(self.env["ir.config_parameter"].sudo().get_param("l10n_cr.atcs"))

        if ntcs and vncs and atcs > 0:
            for patent in self:
                patent.score = (
                    0.6 * (patent.employees or patent.employees_rel) / ntcs
                    + 0.3 * (patent.actives_value or patent.actives_value_rel) / vncs
                    + 0.1 * (patent.sales_value or patent.sales_value_rel) / atcs
                ) * 100
        else:
            raise ValidationError(
                _(
                    "Check the values ​​of the NTcs, VNcs and ATcs fields that cannot be empty.\n"
                    "Go to Settings / Municipality."
                )
            )

    @api.depends("yearly_payment_liqueur")
    def _compute_trimester_payment_liqueur(self):
        for patent in self:
            patent.trimester_payment_liqueur = patent.yearly_payment_liqueur / 4

    @api.depends(
        "yearly_payment", "yearly_payment_rel", "trimester_payment", "trimester_payment_rel"
    )
    def _compute_payment_total(self):
        for patent in self:
            if not patent.needs_liqueur:
                patent.yearly_payment_subtotal = patent.yearly_payment
            else:
                patent.yearly_payment_subtotal = patent.yearly_payment + patent.yearly_payment_rel
            patent.yearly_payment_total = patent.yearly_payment_subtotal + patent.timbre

    @api.depends("type_id")
    def _compute_is_liqueur(self):
        for patent in self:
            patent.is_liqueur = patent.type_code == "LC"

    @api.depends("type_id", "yearly_payment_subtotal")
    def _compute_timbre(self):
        for patent in self:
            patent.timbre = patent.yearly_payment_subtotal * (2 / 100)

    @api.depends("trimester_payment_rel")
    def _compute_yearly_payment_rel(self):
        for patent in self:
            patent.yearly_payment_rel = patent.trimester_payment_rel * 4
            if patent.liqueur_patent_id:
                patent.liqueur_patent_id.yearly_payment = patent.yearly_payment_rel

    def action_view_invoices(self):  # TODO REM
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action["domain"] = [
            ("patent_id", "=", self.id),
        ]
        return action

    def action_view_patent_origin(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "l10n_cr.patent",
            "res_id": self.patent_origin_id.id,
        }

    @api.depends("category_liqueur", "category_liqueur_rel")
    def _compute_liqueur_open_hour(self):
        for patent in self:
            if patent.category_liqueur == "A" or patent.category_liqueur == "B1":
                o_temp = "11"
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == "A" or patent.category_liqueur_rel == "B1":
                o_temp = "11"
                patent.liqueur_open_hour_rel = float(o_temp)

            if patent.category_liqueur == "B2":
                o_temp = "16"
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == "B2":
                o_temp = "16"
                patent.liqueur_open_hour_rel = float(o_temp)

            if patent.category_liqueur == "C":
                o_temp = "11"
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == "C":
                o_temp = "11"
                patent.liqueur_open_hour_rel = float(o_temp)

            if patent.category_liqueur == "D1" or patent.category_liqueur == "D2":
                o_temp = "8"
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == "D1" or patent.category_liqueur_rel == "D2":
                o_temp = "8"
                patent.liqueur_open_hour_rel = float(o_temp)

            if (
                patent.category_liqueur == "E1A"
                or patent.category_liqueur == "E1B"
                or patent.category_liqueur == "E2"
                or patent.category_liqueur == "E3"
                or patent.category_liqueur == "E4"
                or patent.category_liqueur == "E5"
            ):
                o_temp = "00"
                patent.liqueur_open_hour = float(o_temp)
            if (
                patent.category_liqueur_rel == "E1A"
                or patent.category_liqueur_rel == "E1B"
                or patent.category_liqueur_rel == "E2"
                or patent.category_liqueur_rel == "E3"
                or patent.category_liqueur_rel == "E4"
                or patent.category_liqueur_rel == "E5"
            ):
                o_temp = "00"
                patent.liqueur_open_hour_rel = float(o_temp)

    @api.depends("category_liqueur", "category_liqueur_rel")
    def _compute_liqueur_close_hour(self):
        for patent in self:
            if patent.category_liqueur == "A" or patent.category_liqueur == "B1":
                c_temp = "00"
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == "A" or patent.category_liqueur_rel == "B1":
                c_temp = "00"
                patent.liqueur_close_hour_rel = float(c_temp)

            if patent.category_liqueur == "B2":
                c_temp = "2.5"
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == "B2":
                c_temp = "2.5"
                patent.liqueur_close_hour_rel = float(c_temp)
            if patent.category_liqueur == "C":
                c_temp = "2.5"
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == "C":
                c_temp = "2.5"
                patent.liqueur_close_hour_rel = float(c_temp)

            if patent.category_liqueur == "D1" or patent.category_liqueur == "D2":
                c_temp = "00"
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == "D1" or patent.category_liqueur_rel == "D2":
                c_temp = "00"
                patent.liqueur_close_hour_rel = float(c_temp)

            if (
                patent.category_liqueur == "E1A"
                or patent.category_liqueur == "E1B"
                or patent.category_liqueur == "E2"
                or patent.category_liqueur == "E3"
                or patent.category_liqueur == "E4"
                or patent.category_liqueur == "E5"
            ):
                c_temp = "00"
                patent.liqueur_close_hour = float(c_temp)
            if (
                patent.category_liqueur_rel == "E1A"
                or patent.category_liqueur_rel == "E1B"
                or patent.category_liqueur_rel == "E2"
                or patent.category_liqueur_rel == "E3"
                or patent.category_liqueur_rel == "E4"
                or patent.category_liqueur_rel == "E5"
            ):
                c_temp = "00"
                patent.liqueur_close_hour_rel = float(c_temp)

    def process(self):
        self.ensure_one()
        self.state = "in_progress"

    def approve(self):
        self.ensure_one()
        #self.date_approved = datetime.now().date()
        # TODO permissions
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "l10n_cr.patent.approve_wizard",
            "target": "new",
        }

    def reject(self):
        self.ensure_one()
        self.generate_number_resolution()
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "l10n_cr.patent.reject_wizard",
            "target": "new",
        }


    def _get_trimester_percentage_left(self):
        if self.date_approved:
            fecha = self.date_approved
        else:
            fecha = date.today()
        last_month = trimester_to_paid[month_to_trimester[str(fecha.month)]]
        monthRange = calendar.monthrange(datetime.now().year, last_month)

        first_day = date(datetime.now().year,last_month-2,1)
        last_day = date(datetime.now().year, last_month, monthRange[1])
        total_day = (last_day - first_day).days
        days_to_end = (last_day - fecha).days
        return days_to_end / total_day

    def print_approve(self):
        self.ensure_one()

        self.amount_prorate = self.trimester_payment * self._get_trimester_percentage_left()

        if self.state == "approved":
            # GENERAR NÚMERO DE RESOLUCIÓN.
            self.generate_number_resolution()
            if self.type_id.name == "Licores":
                return self.env.ref("l10n_cr_municipality.report_patent_aprob_licor").report_action(
                    self
                )
            else:
                return self.env.ref("l10n_cr_municipality.report_patent_aprob_mcr").report_action(
                    self
                )

    def print_reject(self):
        self.ensure_one()
        if self.state == "rejected":
            # GENERAR NÚMERO DE RESOLUCIÓN.
            self.generate_number_resolution()
            if self.type_id.name == "Licores":
                return self.env.ref("l10n_cr_municipality.report_patent_deneg_licor").report_action(
                    self
                )
            else:
                return self.env.ref("l10n_cr_municipality.report_patent_deneg_mcr").report_action(
                    self
                )

    def generate_number_resolution(self):
        if not self.number_resolution:
            new_code = self.env["ir.sequence"].next_by_code("resolucion.patent")
            self.number_resolution = new_code
        elif self.number_resolution:
            number_resolution = self.number_resolution.split('-')
            if len(number_resolution) > 1:
                self.number_resolution = number_resolution[0]

    def print_cert(self):
        #self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Autorización'),
            'res_model': 'patent.certificate.autorization.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id,'default_patent_id': self.id},
            'views': [[False, 'form']]
        }
        # if self.state == "approved":
        #     if self.type_id.name == "Licores":
        #         self.code_letter = CATEG[self.category_liqueur]
        #         return self.env.ref("l10n_cr_municipality.patent_certificate_licor").report_action(self)
        #     else:
        #         return self.env.ref("l10n_cr_municipality.patent_certificate").report_action(self)

    def action_view_sale(self):
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order",
            "res_id": self.sale_id.id,
            "target": "current",
        }

    def _set_yearly_payment(self):
        for patent in self:
            patent.yearly_payment = patent.trimester_payment * 4

    @api.onchange("is_liqueur", "needs_liqueur")
    def _unlink_subpatent(self):
        if (self.is_liqueur or not self.needs_liqueur) and self.liqueur_patent_id:
            self.needs_liqueur = False
            self.liqueur_patent_id = None
            return {
                "warning": {
                    "title": _("Advertencia"),
                    "message": _("Esto desvinculará la patente de licor existente"),
                }
            }


    def generate_number_prevention(self,type):
        self.prevention_type = type
        # year_now = date.today().year
        if not self.number_preventive:
            new_code = self.env["ir.sequence"].next_by_code("patent.preventive")
            self.number_preventive = new_code
        elif self.number_preventive:
            number_preventive = self.number_preventive.split('-')
            if len(number_preventive) > 1:
                self.number_preventive = number_preventive[0]



    def state_prevention(self):
        self.ensure_one()
        self.state = "prevention"

    def print_prevention(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            'context': {'default_patent_id': self.id},
            "res_model": "patent.select.prevention.wizard",
            "target": "new",
        }

    def state_cancel(self):
        self.ensure_one()
        self.state = "canceled"


