# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    clave_stcc = fields.Char(string='Clave STCC')
    dimensiones = fields.Char(string='Dimensiones XX/XX/XXcm')
    materialpeligroso = fields.Selection(
        selection=[('Sí', 'Si'),
                   ('No', 'No'),],
        string=_('Material peligroso'),
    )
    embalaje = fields.Many2one('cve.tipo.embalaje', string='Embalaje')
    desc_embalaje = fields.Char(string='Descripción de embalaje')
    clavematpeligroso = fields.Many2one('cve.material.peligroso',string='Clave material peligroso')

    SectorCofepris = fields.Many2one('ccp.sector.cofepris',string='Regimen aduanero')
    IngredienteActivo = fields.Char(string=_('Nombre Ingrediente Activo'))
    NomQuimico = fields.Char(string=_('Nombre Quimico'))
    DenominacionGenerica  = fields.Char(string=_('Denominacion Generica'))
    DenominacionDistintiva  = fields.Char(string=_('Denominacion Distintiva'))
    Fabricante  = fields.Char(string=_('Fabricante'))
    FechaCaducidad = fields.Date(string=_('Fecha Caducidad'))
    LoteMedicamento  = fields.Char(string=_('Lote Medicamento'))
    FormaFarmaceutica = fields.Many2one('ccp.forma.farma',string='Forma Farmaceutica')
    CondicionesEsp = fields.Many2one('ccp.condiciones.esp',string='Condiciones Especiales transp.')
    RegistroSanitario  = fields.Char(string=_('Registro Sanitario Folio Autorización'))
    PermisoImportacion  = fields.Char(string=_('Permiso Importacion'))
    FolioImpoVUCEM  = fields.Char(string=_('Folio Impo VUCEM'))
    NumCAS  = fields.Char(string=_('Numero CAS'))
    RazonSocialEmpImp  = fields.Char(string=_('Razon Social Emp Imp'))
    NumRegSan  = fields.Char(string=_('Num Reg San plag COFEPRIS'))
    DatosFabricante  = fields.Char(string=_('Datos Fabricante'))
    DatosFormulador  = fields.Char(string=_('Datos Formulador'))
    DatosMaquilador  = fields.Char(string=_('Datos Maquilador'))
    UsoAutorizado  = fields.Char(string=_('Uso Autorizado'))
    TipoMateria  = fields.Many2one('ccp.tipo.materia',string='Tipo Materia')
    DescripcionMateria  = fields.Char(string=_('Descripción Materia'))
