from odoo import models, fields, api, _


class ESBTRMTR(models.Model):
    _name = 'esbtr.mtr'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'ESBTR/MTR'
    _rec_name = 'app_id'

    sr_no = fields.Integer("SR.NO")
    lan_no = fields.Char("LAN No")
    customer_name = fields.Char("Customer Name")
    loan_amount = fields.Float("Loan Amount")
    em_amount = fields.Float("EM Amount")
    cpc = fields.Many2one("res.partner", "CPC")
    product_id = fields.Many2one("product.product", "Product")
    grn_no = fields.Char("GRN No")
    tran_id = fields.Char("Tran ID")
    data_date = fields.Date("Data Date")
    precessing_date = fields.Date("Processing Date")
    funds_receive_date = fields.Date("Funds Receive Date")
    submission_date = fields.Date("Submission Date")
    comments = fields.Char("Comments")
    acknowledgement = fields.Binary("Acknowledgement")
    freeze_all = fields.Boolean("Freeze All", copy=False)
    app_id = fields.Char(string="App ID", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])

            if not vals.get('app_id'):
                vals['app_id'] = self.env['ir.sequence'].next_by_code('esbtr.seq') or _("New")
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
