from odoo import models, fields, api, _


class VendorPaymentConfirmation(models.Model):
    _name = 'vendor.payment.confirmation'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Vendor Payment Confirmation'
    _rec_name = "name"

    name = fields.Char("Name", tracking=True)