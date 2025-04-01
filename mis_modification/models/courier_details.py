from odoo import models, fields, api, _


class CourierDetails(models.Model):
    _name = 'courier.details'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Courier Details'

    sr_no = fields.Integer("SR.NO")
    courier_company_name = fields.Many2one("res.partner", "Courier Company Name")
    courier_to = fields.Char("Courier To")
    name_of_person = fields.Char("Name of Person")
    address = fields.Char("Address")
    mob_no = fields.Char("Mob No")
    docket_details = fields.Char("Docket Details")
    particulars = fields.Char("Particulars")
    remarks = fields.Char("Remarks")
    freeze_all = fields.Boolean("Freeze All", copy=False)

    def action_submit(self):
        self.write({'freeze_all': True})

    def action_reset_to_draft(self):
        self.write({'freeze_all': False})