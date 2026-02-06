# -*- coding: utf-8 -*-


from odoo import models, fields
from datetime import datetime, timedelta

PE_RELATED_DOCUMENT = [
    ('01', 'Factura'),
    ('03', 'Boleta de Venta'),
    ('04', 'Liquidación de Compra'),
    ('09', 'Guía de Remisión Remitente'),
    ('12', 'Ticket o cinta emitido por máquina registradora'),
    ('31', 'Guía de Remisión Transportista'),
    ('48', 'Comprobante de Operaciones - Ley N° 29972'),
    ('49', 'Constancia de Depósito - IVAP (Ley 28211)'),
    ('50', 'Declaración Aduanera de Mercancías'),
    ('52', 'Declaración Simplificada (DS)'),
    ('65', 'Autorización de Circulación para transportar MATPEL - Callao'),
    ('66', 'Autorización de Circulación para transporte de carga y mercancías en Lima Metropolitana'),
    ('67', 'Permiso de Operación Especial para el servicio de transporte de MATPEL - MTC'),
    ('68', 'Habilitación Sanitaria de Transporte Terrestre de Productos Pesqueros y Acuícolas'),
    ('69', 'Permiso / Autorización de operación de transporte de mercancías'),
    ('71', 'Resolución de Adjudicación de bienes - SUNAT'),
    ('72', 'Resolución de Comiso de bienes - SUNAT'),
    ('73', 'Guía de Transporte Forestal o de Fauna - SERFOR'),
    ('74', 'Guía de Tránsito - SUCAMEC'),
    ('75', 'Autorización para operar como empresa de Saneamiento Ambiental - MINSA'),
    ('76', 'Autorización para manejo y recojo de residuos sólidos peligrosos y no peligrosos'),
    ('77', 'Certificado fitosanitario la movilización de plantas, productos vegetales, y otros artículos reglamentados'),
    ('78', 'Registro Único de Usuarios y Transportistas de Alcohol Etílico'),
    ('80', 'Constancia de Depósito - Detracción'),
    ('81', 'Código de autorización emitida por el SCOP'),
    ('82', 'Declaración jurada de mudanza'),
]


class Picking(models.Model):
    _inherit = "stock.picking"
        
    l10n_pe_edi_reason_for_transfer = fields.Selection(selection_add=[('06', 'Devolución')], ondelete={'peppol': 'cascade'})
    
    
    def do_print_picking(self):
        self.write({'printed': True})
        return self.env.ref('l10n_pe_edi_stock_pdf.action_report_picking_guide_pdf').report_action(self)

    def get_tipo_doc_relacionado(self):
        return dict(PE_RELATED_DOCUMENT)[self.l10n_pe_edi_related_document_type] if self.l10n_pe_edi_related_document_type else False