from odoo import models, fields, api, _


class BTPropertyCollection(models.Model):
    _name = 'bt.property.collection'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'BT/ Property Paper Collection'
    _rec_name = 'app_id'


    sr_no = fields.Integer("SR.NO",tracking=True)
    app_id = fields.Char(string="App ID",readonly=True,tracking=True)
    lan_no = fields.Char("LAN No",tracking=True)
    cpc = fields.Many2one("res.partner", "CPC",tracking=True)
    customer_name = fields.Char("Customer Name",tracking=True)
    description = fields.Char("Description",tracking=True)
    document_receive_date = fields.Date("Document Receive date",tracking=True)
    transaction_type = fields.Char("Transaction Type",tracking=True)
    previous_finance_name = fields.Char("Previous Finance Name & Branch",tracking=True)
    property_address = fields.Char("Property Address",tracking=True)
    communication_address = fields.Char("Communication Address",tracking=True)
    contact_no_1 = fields.Char("Contact 1",tracking=True)
    contact_no_2 = fields.Char("Contact 2",tracking=True)
    sm_name = fields.Char("SM Name",tracking=True)
    data_shared_with_agency = fields.Date("Date - Data Shared with Agency",tracking=True)
    calling_remarks = fields.Char("Calling Remarks",tracking=True)
    next_followup_date = fields.Date("Next Followup Date",tracking=True)
    document_status = fields.Char("Document Status",tracking=True)
    document_submission_date = fields.Date("Document Submission Date",tracking=True)
    freeze_all = fields.Boolean("Freeze All", copy=False,tracking=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])

            if not vals.get('app_id'):
                vals['app_id'] = self.env['ir.sequence'].next_by_code('bt.property.seq') or _("New")
                print("seqeuce generated:::", vals['app_id'])
        return super().create(vals_list)

    _sql_constraints = [
        ('app_id_unique', 'unique(app_id)', 'App ID must be unique.'),
        ('app_id_not_null', 'CHECK(app_id IS NOT NULL)', 'App ID cannot be null.'), ]

    def action_submit(self):
        self.write({'freeze_all': True})

    def action_reset_to_draft(self):
        self.write({'freeze_all': False})