from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang
from datetime import date, timedelta


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    l10n_pe_document_type_id = fields.Many2one('l10n_latam.document.type', string='Tipo de documento')
