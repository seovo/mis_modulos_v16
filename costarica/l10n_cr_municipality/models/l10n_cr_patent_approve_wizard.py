from datetime import date, datetime

from odoo import _, api, fields, models
from odoo.tools import date_utils

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

trimester_to_number = {
    "t1": 1,
    "t2": 2,
    "t3": 3,
    "t4": 4,
}


class PatentApproveWizard(models.TransientModel):
    _name = "l10n_cr.patent.approve_wizard"
    _description = "CR Patent Invoice Wizard"


    patent_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        # required=True,
        default=lambda self: self.env["l10n_cr.patent"].browse(self._context["active_id"]),
        readonly=True,
    )
    full_year = fields.Boolean(
        string="Año completo",
    )
    apply_discount = fields.Boolean(
        string="Aplicar Descuento",
    )

    def _default_trimester(self):
        month_now = datetime.now().date().month
        return month_to_trimester[str(month_now)]

    trimester = fields.Selection(
        selection=[
            ("t1", "Primer Trimestre"),
            ("t2", "Segundo Trimestre"),
            ("t3", "Tercer Trimestre"),
            ("t4", "Cuarto Trimestre"),
        ],
        string="Trimestre",
        required=True,
        default=_default_trimester,
    )

    @api.onchange("trimester")
    def _change_trimester(self):
        if self.trimester:
            if self.trimester != "t4":  # SIEMPRE Y CUANDO EL TRIMESTRE SEA 4 NO APLICA DESCUENTO
                self.apply_discount = False

    def _get_trimesters(self):
        actual_month = str(datetime.now().date().month)
        actual_trimester_number = trimester_to_number[month_to_trimester[actual_month]]

        trimester_number = trimester_to_number[self.trimester]
        payed_to_month_number = str(self.patent_id.pay_to.month if self.patent_id.pay_to else None)
        payed_to_trimester = month_to_trimester.get(payed_to_month_number, None)
        payed_to_trimester_number = trimester_to_number.get(payed_to_trimester, 0)

        discount = float(
            self.env["ir.config_parameter"].sudo().get_param("l10n_cr.payment_in_advance_discount")
        )
        trimesters = [
            {
                "name": _(f"Patente {self.patent_id.name} trimestre {t+1}"),
                "discount": discount if self.apply_discount else 0,
                "account_id": self.patent_id.company_id.advance_account_id.id if t > 0 else [],
                "advance": t > (actual_trimester_number - 1),
            }
            for t in range(payed_to_trimester_number, trimester_number)
        ]
        return trimesters

    def _get_trimester_percentage_left(self):
        first_day = date(2021, 1, 1)
        last_day = date(2021, 3, 31)
        total_day = (last_day - first_day).days
        days_to_end = (last_day - fields.Date.today()).days
        return days_to_end / total_day

    def _get_sale_lines(self):
        trimesters = self._get_trimesters()
        trimester_percentage_left = self._get_trimester_percentage_left()
        lines = [
            {  # TODO compute
                "product_id": (
                    self.patent_id.type_id.product_advance_id
                    if trimester["advance"]
                    else self.patent_id.type_id.product_id
                ).id,
                "name": trimester["name"],
                "price_unit": self.patent_id.trimester_payment
                * (1 if trimester["advance"] else trimester_percentage_left),
                "discount": trimester["discount"],
            }
            for trimester in trimesters
        ]
        timbre_percentage = len(trimesters) / 4
        lines.append(
            {
                "product_id": self.env.ref("l10n_cr_municipality.product_timbre").id,
                "price_unit": self.patent_id.timbre * timbre_percentage,
            }
        )
        return [(0, None, line) for line in lines]

    def create_sale(self):
        lines = self._get_sale_lines()
        sale_data = {
            "partner_id": self.patent_id.partner_id.id,
            "patent_id": self.patent_id.id,
            "order_line": lines,
        }
        sale = self.env["sale.order"].create(sale_data)
        return sale

    def get_pay_to(self, today):
        last_day = date(today.year, 12, 31)
        trim = date_utils.get_quarter(today)
        if self.trimester == "t4":
            self.full_year = True
            return last_day

        return trim[1]



    def approve(self):
        today = fields.Date.today()
        pay_to = self.get_pay_to(today)

        for wizard in self:
            wizard.patent_id.sale_id = wizard.create_sale()
            wizard.patent_id.sale_id.action_confirm()
            invoices = wizard.patent_id.sale_id._create_invoices()
            invoices.action_post()
            invoices.patent_id = wizard.patent_id
            wizard.patent_id.state = "approved"
            wizard.patent_id.resolution_date = fields.Date.today()
            wizard.patent_id.pay_to = pay_to

            # CREACION DE SECUENCIA PARA RESOLUCION

            if len(self) == 1:
                return wizard.patent_id.sale_id.action_view_invoice()
        return {}
