import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import pager as portal_pager

class CustomerPortal(payment_portal.PaymentPortal):

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, **kwargs):
        values = self._prepare_checklist_portal_rendering_values(quotation_page=False, **kwargs)
        request.session['my_pickings_history'] = values['pickings'].ids[:100]
        return request.render("eventos_prociencia_jz.portal_my_pickings", values)

    @http.route(['/my/checklist', '/my/checklist/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_checklist(self, **kwargs):
        values = self._prepare_checklist_portal_rendering_values(quotation_page=False, **kwargs)
        request.session['my_pickings_history'] = values['pickings'].ids[:100]
        return request.render("eventos_prociencia_jz.portal_my_pickings", values)

    def _prepare_checklist_domain(self, partner):
        return [
            ('event_line_ids','!=',False),
            #"('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            #('state_event','!=','done'),
            #('state_event','!=',False)
            ('state', '=', 'sale'),
        ]

    def _get_checklist_searchbar_sortings(self):
        return {
            'stage': {'label': _('Stage'), 'order': 'state_event desc'},
            'date': {'label': _('Date'), 'order': 'date_event desc'},
            'name': {'label': _('Reference'), 'order': 'name'},

        }

    def _prepare_checklist_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, **kwargs
    ):
        StockPicking = request.env['sale.order'].sudo()

        if not sortby:
            sortby = 'date'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        if quotation_page:

            domain = self._prepare_checklist_domain(partner)
        else:

            domain = self._prepare_checklist_domain(partner)

        searchbar_sortings = self._get_checklist_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url='/my/checklist',
            total=StockPicking.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        orders = StockPicking.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            #'quotations': orders.sudo() if quotation_page else SaleOrder,
            #'orders': orders.sudo() if not quotation_page else SaleOrder,
            'pickings': orders.sudo(),
            'page_name': 'picking' ,
            'pager': pager_values,
            'default_url': '/my/checklist',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_myyorders(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        return self.portal_checklist_page(order_id, report_type=None, access_token=None, message=False, download=False, **kw)

    @http.route(['/my/checklist/<int:order_id>'], type='http', auth="public", website=True)
    def portal_checklist_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        picking_sudo = request.env['sale.order'].sudo().search([('id','=',int(order_id))])

        #try:
        #    picking_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        #except (AccessError, MissingError):
        #    return request.redirect('/my')

        #imprimir reporte

        #if report_type in ('html', 'pdf', 'text'):
        #    return self._show_report(model=order_sudo, report_type=report_type,
        #                             report_ref='sale.action_report_saleorder', download=download)

        '''
        if request.env.user.share and access_token:
            # If a public/portal user accesses the order with the access token
            # Log a note on the chatter.
            today = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if session_obj_date != today:
                # store the date as a string in the session to allow serialization
                request.session['view_quote_%s' % order_sudo.id] = today
                # The "Quotation viewed by customer" log note is an information
                # dedicated to the salesman and shouldn't be translated in the customer/website lgg
                context = {'lang': order_sudo.user_id.partner_id.lang or order_sudo.company_id.partner_id.lang}
                msg = _('Quotation viewed by customer %s',
                        order_sudo.partner_id.name if request.env.user._is_public() else request.env.user.partner_id.name)
                del context
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    message=msg,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )
                
        '''

        ''''''

        backend_url = f'/web#model={picking_sudo._name}' \
                      f'&id={picking_sudo.id}' \
                      f'&action={picking_sudo._get_portal_return_action().id}' \
                      f'&view_type=form'
        values = {
            'page_name': 'picking',
            'picking': picking_sudo,
            #'message': message,
            #'report_type': 'html',
            'backend_url': backend_url,
            #'res_company': order_sudo.company_id,  # Used to display correct company logo
        }

        # Payment values
        #if order_sudo._has_to_be_paid():
        #    values.update(self._get_payment_values(order_sudo))

        #if order_sudo.state in ('draft', 'sent', 'cancel'):
        #    history_session_key = 'my_quotations_history'
        #else:
        #    history_session_key = 'my_orders_history'





        history_session_key = 'my_pickings_history'




        values = self._get_page_view_values(
            picking_sudo, access_token, values, history_session_key, False)

        return request.render('eventos_prociencia_jz.picking_portal_template', values)

    ################
    @http.route('/picking/update/event', type='json', auth='public', methods=['POST'], website=True)
    def picking_update_event(
            self, picking_id, state, force=False ,
            **kwargs
    ):
        picking = request.env['sale.order'].sudo().browse(int(picking_id))

        state_event = picking.state_event

        total_done = 0
        completed = True

        for line in picking.event_line_ids:

            if line.display_type :
                continue

            total_done += 1

            if state_event == 'in_progress':
                if not line.check1:
                    completed = False
            if state_event == 'embarked':
                if not line.check2 and line.check1:
                    completed = False

            if state_event == 'collect':
                if not line.check3 :
                    completed = False



        if not completed and force:
            completed = True

        #if state in ['embarked', 'transported']:
        #    completed = True

        if total_done > 0 and completed:
            state_new = None
            if state == 'in_progress':
                state_new = 'embarked'
            if state == 'embarked':
                state_new = 'collect'

            if state == 'collect':
                state_new = 'done'

            if state_new:
                picking.state_event = state_new



        return {
            'total_done': total_done ,
            'completed': completed
        }



    @http.route('/move/check/update', type='json', auth='public', methods=['POST'], website=True)
    def move_check_update(
            self, move_id, qty, checked,
            **kwargs
    ):
        move = request.env['sale.order.items.event'].sudo().browse(int(move_id))

        if not qty:

            is_check = bool(checked)

            if move.order_id.state_event == 'in_progress':
                move.check1 = is_check
                move.user1 = request.env.user.id

            if move.order_id.state_event == 'embarked':
                move.check2 = is_check
                move.user2 = request.env.user.id

            if move.order_id.state_event == 'collect':
                move.check3 = is_check
                move.user3 = request.env.user.id

        else:
            move.quantity = int(qty)
            if int(qty) >= move.product_uom_qty :
                checked = True




        return {
            'checked': checked ,
            #'qty': move.quantity ,


        }
        return [move_id,qty,checked]
