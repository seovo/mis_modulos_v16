from odoo import api, fields, models , _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @contextmanager
    def _check_balanced(self, container):
        return
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
            yield
            if disabled:
                return

        if unbalanced_moves := self._get_unbalanced_moves(container):
            if len(unbalanced_moves) == 1:
                raise UserError(_("The entry is not balanced."))

            error_msg = _("The following entries are unbalanced:\n\n")
            for move in unbalanced_moves:
                error_msg += f"  - {self.browse(move[0]).name}\n"

            raise UserError(error_msg)

    def set_compute_amount(self):
        self._compute_amount()