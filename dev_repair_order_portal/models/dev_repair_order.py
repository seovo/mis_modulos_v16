# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date, timedelta

class dev_web_repair_order(models.Model):
    _name = 'repair.order'
    _inherit = ['portal.mixin' ,'repair.order']
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (_('Repair Order'), self.name)

    def _compute_access_url(self):
        super(dev_web_repair_order, self)._compute_access_url()
        for order in self:
            order.access_url = '/my/repair_order/%s' % (order.id)
    
# vim:expandtab:smartindent:tabstop=4:4softtabstop=4:shiftwidth=4:
