from odoo import models, fields, api, _


class VendorRemarks(models.Model):
    _name = 'vendor.remarks'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Vendor Remarks'
    _rec_name = "name"

    name = fields.Char("Name", tracking=True)