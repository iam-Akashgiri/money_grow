from odoo import models, fields, api, _


class ShareCertificate(models.Model):
    _name = 'share.certificate'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Share Certificate'
    _rec_name = 'app_id'


    sr_no = fields.Integer("SR.NO")
    lan_no = fields.Char("LAN No")
    app_id = fields.Char(string="App ID",readonly=True)

    cpc = fields.Many2one("res.partner", "CPC")
    customer_contact_no = fields.Char("Customer Contact No")
    customer_name = fields.Char("Customer Name")
    secretary_name = fields.Char("Secretary Name")
    secretary_contact_no = fields.Char("Secretary contact No")
    property_address = fields.Char("Property Address")
    data_shared_with_agency = fields.Date("Date - Data Shared with Agency")
    calling_remarks = fields.Char("Calling Remarks")
    next_followup_date = fields.Date("Next Followup Date")
    document_status = fields.Char("Document Status")
    share_certificate_receive_date = fields.Date("Share Certificate Receive Date")
    share_certificate_submission_date = fields.Date("Share Certificate Submission Date")
    remarks = fields.Char("Remarks")
    share_certificate_society_sub_date = fields.Date("Share Certificate Society Submission Date")
    freeze_all = fields.Boolean("Freeze All", copy=False)

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
