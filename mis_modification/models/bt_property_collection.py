from odoo import models, fields, api, _


class BTPropertyCollection(models.Model):
    _name = 'bt.property.collection'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'BT/ Property Paper Collection'

    sr_no = fields.Integer("SR.NO")
    lan_no = fields.Char("LAN No")
    cpc = fields.Many2one("res.partner", "CPC")
    customer_name = fields.Char("Customer Name")
    description = fields.Char("Description")
    document_receive_date = fields.Date("Document Receive date")
    transaction_type = fields.Char("Transaction Type")
    previous_finance_name = fields.Char("Previous Finance Name & Branch")
    property_address = fields.Char("Property Address")
    communication_address = fields.Char("Communication Address")
    contact_no_1 = fields.Char("Contact 1")
    contact_no_2 = fields.Char("Contact 2")
    sm_name = fields.Char("SM Name")
    data_shared_with_agency = fields.Date("Date - Data Shared with Agency")
    calling_remarks = fields.Char("Calling Remarks")
    next_followup_date = fields.Date("Next Followup Date")
    document_status = fields.Char("Document Status")
    document_submission_date = fields.Date("Document Submission Date")
    freeze_all = fields.Boolean("Freeze All", copy=False)

    def action_submit(self):
        self.write({'freeze_all': True})

    def action_reset_to_draft(self):
        self.write({'freeze_all': False})