import json
import requests
from odoo import models, fields, api

tipos_documento = {
    'FACTURA': 1,
    'BOLETA': 2,
    'NOTA DE CRÉDITO': 3,
    'NOTA DE DÉBITO': 4
}

tipos_operacion = {
    '0101': 1,
    'EXPORTACIÓN': 2,
    'VENTA INTERNA – ANTICIPOS': 4,
    'VENTAS NO DOMICILIADOS QUE NO CALIFICAN COMO EXPORTACIÓN': 29,
    'OPERACIÓN SUJETA A DETRACCIÓN': 30,
    'DETRACCIÓN - RECURSOS HIDROBIOLÓGICOS': 31,
    'DETRACCIÓN - SERVICIOS DE TRANSPORTE DE PASAJEROS': 32,
    'DETRACCIÓN - SERVICIOS DE TRANSPORTE CARGA': 33,
    'OPERACIÓN SUJETA A PERCEPCIÓN': 34,
    'VENTA NACIONAL A TURISTAS - TAX FREE': 35
}

tipos_moneda = {
    'PEN': 1,
    'USD': 2,
    'EUR': 3,
    'GBP': 4
}

class NubefactAPI(models.Model):
    _name = 'nubefact.api'
    _description = 'Conector Nubefact'

    @api.model
    def send_nubefact(self, invoice, vals):
        company = invoice.company_id
        url = company.l10n_pe_edi_provider_url
        token = company.l10n_pe_edi_provider_token

        # Extraer datos de vals para armar el JSON de Nubefact
        vals_data = vals.get('vals', {})
        supplier = vals.get('supplier')
        customer = vals.get('customer')
        taxes = vals.get('taxes_vals', {})
        monetary_total = vals_data.get('monetary_total_vals', {})
        line_vals = vals_data.get('line_vals', [])

        # Mapear tipo de comprobante (ejemplo: factura = "1")
        tipo_de_comprobante = "1" if vals.get('document_type') == 'invoice' else "0"

        # Serie y número
        serie, numero = vals_data.get('id', '').split('-') if '-' in vals_data.get('id', '') else ('', '')

        # Cliente
        cliente_tipo_de_documento = customer.l10n_latam_identification_type_id.l10n_pe_vat_code or ''
        cliente_numero_de_documento = customer.vat or ''
        cliente_denominacion = customer.name or ''
        cliente_direccion = customer.street or ''

        # Fechas
        fecha_de_emision = vals_data.get('issue_date').strftime("%d-%m-%Y") if vals_data.get('issue_date') else fields.Date.today().strftime("%d-%m-%Y")

        # Moneda
        moneda = "1" if (vals_data.get('currency_code') or '').upper() == "PEN" else "2"

        # IGV
        porcentaje_de_igv = taxes.get('tax_details', {}).keys()
        # Tomar el primer tax_detail para obtener el porcentaje
        tax_percent = 18.0
        for k in taxes.get('tax_details', {}):
            tax_percent = k.get('tax_category_percent', 18.0)
            break
        porcentaje_de_igv = tax_percent

        # Totales
        total_gravada = monetary_total.get('tax_exclusive_amount', 0)
        total_igv = vals['taxes_vals'].get('tax_amount', 0)
        total = monetary_total.get('payable_amount', 0)

        # Items
        items = []
        for line in line_vals:
            igv = sum(l['tax_amount'] for l in line['tax_total_vals'])
            items.append({
            "unidad_de_medida": line['line_quantity_attrs'].get('unitCode', 'NIU'),
            "codigo": line['item_vals']['sellers_item_identification_vals']['id'],
            "descripcion": line['item_vals']['description'],
            "cantidad": line.get('line_quantity', 1),
            "valor_unitario": line['price_vals']['price_amount'],
            "precio_unitario": line['price_vals']['price_amount'] + igv,
            "subtotal": line['pricing_reference_vals']['alternative_condition_price_vals'][0]['price_amount']
,
            "tipo_de_igv": 1,  # Ajustar según tax
            "igv": igv,
            "total": igv,
            "anticipo_regularizacion": False,
            })

        data = {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante":  tipos_documento.get(vals['invoice'].l10n_latam_document_type_id.name.upper(), 1),
            "serie": serie,
            "numero": int(numero),
            "sunat_transaction": tipos_operacion.get(vals['invoice'].l10n_pe_edi_operation_type,1),
            "cliente_tipo_de_documento": cliente_tipo_de_documento,
            "cliente_numero_de_documento": cliente_numero_de_documento,
            "cliente_denominacion": cliente_denominacion,
            "cliente_direccion": cliente_direccion,
            "fecha_de_emision": fecha_de_emision,
            "moneda": tipos_moneda.get(vals['invoice'].currency_id.name, 1),
            "porcentaje_de_igv": porcentaje_de_igv,
            "total_gravada": total_gravada,
            "total_igv": total_igv,
            "total": total,
            "detraccion": False,
            "enviar_automaticamente_a_la_sunat": True,
            "enviar_automaticamente_al_cliente": False,
            "items": items
        }

        headers = {
            'Authorization': f'Token token="{token}"',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()

        if 'errors' in result:
            raise Exception(f"Error en Nubefact: {result['errors']}")

        return result
