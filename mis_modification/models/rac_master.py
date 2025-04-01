from odoo import models, fields, api, _


class RACRemarks(models.Model):
    _name = 'rac.remarks'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'RAC Remarks'
    _rec_name = "name"

    name = fields.Char("Name", tracking=True)