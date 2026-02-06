# -*- coding: utf-8 -*-

from odoo import models, api, fields

class ReportOperacionReportLiquidacion(models.AbstractModel):
    _name = 'report.operations_management.report_operacion_liquidacion'
    _description = 'Operacion Liquidacion Report'


    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['operacion.liquidacion'].browse(docids)
        # liquidacion = self.env['operacion.liquidacion'].browse(data['context']['active_id'])
        liquidacion = self.env['operacion.liquidacion'].browse(docids)
        liquidacion_line = liquidacion.line_ids[0]
        data.update({
            'cedente': {'name': liquidacion_line.cedente_id.name, 'ruc': liquidacion_line.cedente_id.vat},
            'proveedor': {'name': liquidacion_line.proveedor_id.name, 'ruc': liquidacion_line.proveedor_id.vat},
            'deudor': {'name': liquidacion_line.deudor_id.name, 'ruc': liquidacion_line.deudor_id.vat},
            'date':fields.Date.today(),
            'tem': liquidacion_line.por_tem,
        })
        lines, totals = self._get_liquidacion_lines(liquidacion)
        data['lines'] = lines
        data['totals'] = totals
        return {
            'doc_ids': docids,
            'doc_model': 'operacion.liquidacion',
            'docs': docs,
            'data': data,
        }
        
    def _get_liquidacion_lines(self, liquidacion):
        lines = []
        item = 0
        for line in liquidacion.line_ids:
            item += 1
            lines.append({
                'item': item,
                'documento': line.documento_id.name,
                'valor_nominal': line.net_amount_document,
                'fecha_desembolso': line.fch_desembolso,
                'fecha_vencimiento': line.fch_vencimiento,
                'dias_financiamiento': (line.fch_vencimiento - line.fch_desembolso).days,
                'importe_garantia': line.monto_fdg,
                'valor_negociable': line.net_amount_document - line.monto_fdg,
                'interes_descuento': 1666.53,
                'importe_valorizado': line.pago_factor,
            })

        totals = {
            'valor_nominal': sum(l['valor_nominal'] for l in lines),
            'importe_garantia': sum(l['importe_garantia'] for l in lines),
            'valor_negociable': sum(l['valor_negociable'] for l in lines),
            'interes_descuento': sum(l['interes_descuento'] for l in lines),
            'importe_valorizado': sum(l['importe_valorizado'] for l in lines),
        }

        return lines, totals
        