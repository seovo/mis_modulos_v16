# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SequenceMixin(models.AbstractModel):

    _inherit = 'sequence.mixin'

    def _set_next_sequence(self):
        """Set the next sequence.

        This method ensures that the field is set both in the ORM and in the database.
        This is necessary because we use a database query to get the previous sequence,
        and we need that query to always be executed on the latest data.

        :param field_name: the field that contains the sequence.
        """
        self.ensure_one()
        if str(self)[:12] == 'account.move':
            if self.move_type in ['out_invoice', 'out_refund']:
                last_sequence = self._get_last_sequence(relaxed=True)
            else:
                last_sequence = self._get_last_sequence()
        else:
            last_sequence = self._get_last_sequence()
        new = not last_sequence
        if new:
            last_sequence = self._get_last_sequence(relaxed=True) or self._get_starting_sequence()

        format, format_values = self._get_sequence_format_param(last_sequence)
        if new:
            format_values['seq'] = 0
            format_values['year'] = self[self._sequence_date_field].year % (10 ** format_values['year_length'])
            format_values['month'] = self[self._sequence_date_field].month
        format_values['seq'] = format_values['seq'] + 1

        self[self._sequence_field] = format.format(**format_values)
        self._compute_split_sequence()

