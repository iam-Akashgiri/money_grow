from odoo import models, fields, api, _


class ShareCertificate(models.Model):
    _name = 'share.certificate'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Share Certificate'
    _rec_name = 'app_id'


    sr_no = fields.Integer("SR.NO",tracking=True)
    lan_no = fields.Char("LAN No",tracking=True)
    app_id = fields.Char(string="App ID",readonly=True,tracking=True)

    cpc = fields.Many2one("res.partner", "CPC",tracking=True)
    customer_contact_no = fields.Char("Customer Contact No",tracking=True)
    customer_name = fields.Char("Customer Name",tracking=True)
    secretary_name = fields.Char("Secretary Name",tracking=True)
    secretary_contact_no = fields.Char("Secretary contact No",tracking=True)
    property_address = fields.Char("Property Address",tracking=True)
    data_shared_with_agency = fields.Date("Date - Data Shared with Agency",tracking=True)
    calling_remarks = fields.Char("Calling Remarks",tracking=True)
    next_followup_date = fields.Date("Next Followup Date",tracking=True)
    document_status = fields.Char("Document Status",tracking=True)
    share_certificate_receive_date = fields.Date("Share Certificate Receive Date",tracking=True)
    share_certificate_submission_date = fields.Date("Share Certificate Submission Date",tracking=True)
    remarks = fields.Char("Remarks",tracking=True)
    share_certificate_society_sub_date = fields.Date("Share Certificate Society Submission Date",tracking=True)
    freeze_all = fields.Boolean("Freeze All", copy=False,tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])

            if not vals.get('app_id'):
                vals['app_id'] = self.env['ir.sequence'].next_by_code('share.seq') or _("New")
                print("seqeuce generated:::", vals['app_id'])
        return super().create(vals_list)

    _sql_constraints = [
        ('app_id_unique', 'unique(app_id)', 'App ID must be unique.'),
        ('app_id_not_null', 'CHECK(app_id IS NOT NULL)', 'App ID cannot be null.'),

    ]

    def action_submit(self):
        self.write({'freeze_all': True})

    def action_reset_to_draft(self):
        self.write({'freeze_all': False})
