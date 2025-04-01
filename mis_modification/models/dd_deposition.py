from odoo import models, fields, api, _


class DDeposition(models.Model):
    _name = 'dd.deposition'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'DDeposition'

    sr_no = fields.Integer("SR.NO")
    data_date_shared = fields.Date("Data Date Shared")
    cpc = fields.Many2one("res.partner", "CPC")
    loan_disb_date = fields.Date("Loan Disb Date")
    lan_no = fields.Char("LAN No")
    customer_name = fields.Char("Customer Name")
    loan_amount = fields.Float("Loan Amount")
    dd_no = fields.Integer("DD No")
    type_of_transaction = fields.Char("Type of Transaction")
    name_of_sales_manager = fields.Char("Name of Sales Manager")
    bt_bank_name = fields.Char("BT Bank Name")
    dd_deposit_name = fields.Char("DD Deposit Name")
    user_id = fields.Many2one("hr.employee", "User")
    attachment = fields.Binary("Attachment")
    freeze_all = fields.Boolean("Freeze All", copy=False)

    def action_submit(self):
        self.write({'freeze_all': True})

    def action_reset_to_draft(self):
        self.write({'freeze_all': False})
