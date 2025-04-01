from odoo import models, fields, api, _


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    email_2 = fields.Char("Email-2", tracking=True)
    email_3 = fields.Char("Email-3", tracking=True)