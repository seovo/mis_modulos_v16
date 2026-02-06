# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import fields, models, _, api, Command, SUPERUSER_ID, modules
from odoo.tools import config, format_amount, plaintext2html, split_every, str2bool
from psycopg2.extensions import TransactionRollbackError
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    auto_published_invoice = fields.Boolean(string="Auto Publicación", default=False)

    def _handle_automatic_invoices(self, invoice, auto_commit):
        if not self.auto_published_invoice:
            self.with_context(mail_notrack=True).write({'payment_exception': True})
            return invoice
        return super(SaleOrder, self)._handle_automatic_invoices(invoice, auto_commit)

    def _create_recurring_invoice(self, batch_size=30):
        today = fields.Date.today()
        auto_commit = not bool(config['test_enable'] or config['test_file'])
        grouped_invoice = self.env['ir.config_parameter'].get_param('sale_subscription.invoice_consolidation', False)
        all_subscriptions, need_cron_trigger = self._recurring_invoice_get_subscriptions(grouped=grouped_invoice, batch_size=batch_size)
        if not all_subscriptions:
            return self.env['account.move']
        # We mark current batch as having been seen by the cron
        all_invoiceable_lines = self.env['sale.order.line']
        for subscription in all_subscriptions:
            subscription.is_invoice_cron = True
            # Don't spam sale with assigned emails.
            subscription = subscription.with_context(mail_auto_subscribe_no_notify=True)
            # Close ending subscriptions
            auto_close_subscription = subscription.filtered_domain([('end_date', '!=', False)])
            closed_contract = auto_close_subscription._subscription_auto_close()
            subscription -= closed_contract
            all_invoiceable_lines += subscription.with_context(recurring_automatic=True)._get_invoiceable_lines()

        lines_to_reset_qty = self.env['sale.order.line']
        account_moves = self.env['account.move']
        move_to_send_ids = []
        # Set quantity to invoice before the invoice creation. If something goes wrong, the line will appear as "to invoice"
        # It prevents the use of _compute method and compare the today date and the next_invoice_date in the compute which would be bad for perfs
        all_invoiceable_lines._reset_subscription_qty_to_invoice()
        self._subscription_commit_cursor(auto_commit)
        for subscription in all_subscriptions:
            if len(subscription) == 1:
                subscription = subscription[0]  # Trick to not prefetch other subscriptions is all_subscription is recordset, as the cache is currently invalidated at each iteration

            # We check that the subscription should not be processed or that it has not already been set to "in exception" by previous cron failure
            # We only invoice contract in sale state. Locked contracts are invoiced in advance. They are frozen.
            subscription = subscription.filtered(lambda sub: sub.subscription_state == '3_progress' and not sub.payment_exception)
            if not subscription:
                continue
            try:
                self._subscription_commit_cursor(auto_commit)  # To avoid a rollback in case something is wrong, we create the invoices one by one
                draft_invoices = subscription.invoice_ids.filtered(lambda am: am.state == 'draft')
                if draft_invoices:
                    draft_invoices.button_cancel()
                invoiceable_lines = all_invoiceable_lines.filtered(lambda l: l.order_id.id in subscription.ids)
                invoice_is_free, is_exception = subscription._invoice_is_considered_free(invoiceable_lines)
                if not invoiceable_lines or invoice_is_free:
                    if is_exception:
                        for sub in subscription:
                            # Mix between recurring and non-recurring lines. We let the contract in exception, it should be
                            # handled manually
                            msg_body = _(
                                "Mix of negative recurring lines and non-recurring line. The contract should be fixed manually",
                                inv=sub.next_invoice_date
                            )
                            sub.message_post(body=msg_body)
                        subscription.payment_exception = True
                    # We still update the next_invoice_date if it is due
                    elif subscription.next_invoice_date and subscription.next_invoice_date <= today:
                        subscription._update_next_invoice_date()
                        if invoice_is_free:
                            for line in invoiceable_lines:
                                line.qty_invoiced = line.product_uom_qty
                            subscription._subscription_post_success_free_renewal()
                    continue

                try:
                    invoice = subscription.with_context(recurring_automatic=True)._create_invoices(final=True)
                    lines_to_reset_qty |= invoiceable_lines
                except Exception as e:
                    # We only raise the error in test, if the transaction is broken we should raise the exception
                    if not auto_commit and isinstance(e, TransactionRollbackError):
                        raise
                    # we suppose that the payment is run only once a day
                    self._subscription_rollback_cursor(auto_commit)
                    for sub in subscription:
                        email_context = sub._get_subscription_mail_payment_context()
                        error_message = _("Error during renewal of contract %s (Payment not recorded)", sub.name)
                        _logger.exception(error_message)
                        body = self._get_traceback_body(e, error_message)
                        mail = self.env['mail.mail'].sudo().create(
                            {'body_html': body, 'subject': error_message,
                             'email_to': email_context['responsible_email'], 'auto_delete': True})
                        mail.send()
                    continue
                self._subscription_commit_cursor(auto_commit)
                # Handle automatic payment or invoice posting

                existing_invoices = subscription.with_context(recurring_automatic=True)._handle_automatic_invoices(invoice, auto_commit) or self.env['account.move']
                account_moves |= existing_invoices
                subscription.with_context(mail_notrack=True).payment_exception = False
                if not subscription.mapped('payment_token_id'): # _get_auto_invoice_grouping_keys groups by token too
                    move_to_send_ids += existing_invoices.ids
            except Exception:
                name_list = [f"{sub.name} {sub.client_order_ref}" for sub in subscription]
                _logger.exception("Error during renewal of contract %s", "; ".join(name_list))
                self._subscription_rollback_cursor(auto_commit)
        self._subscription_commit_cursor(auto_commit)
        self._process_invoices_to_send(self.env['account.move'].browse(move_to_send_ids))
        # There is still some subscriptions to process. Then, make sure the CRON will be triggered again asap.
        if need_cron_trigger:
            self._subscription_launch_cron_parallel(batch_size)
        else:
            self.env['sale.order']._post_invoice_hook()
            failing_subscriptions = self.search([('is_batch', '=', True)])
            failing_subscriptions.write({'is_batch': False})

        return account_moves