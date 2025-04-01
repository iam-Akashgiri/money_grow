from odoo import models, fields, api, _


class DDeposition(models.Model):
    _name = 'dd.deposition'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'DDeposition'
    _rec_name = 'app_id'

    sr_no = fields.Integer("SR.NO",tracking=True)
    app_id = fields.Char(string="App ID", readonly=True,tracking=True)
    data_date_shared = fields.Date("Data Date Shared",tracking=True)
    cpc = fields.Many2one("res.partner", "CPC",tracking=True)
    loan_disb_date = fields.Date("Loan Disb Date",tracking=True)
    lan_no = fields.Char("LAN No",tracking=True)
    customer_name = fields.Char("Customer Name",tracking=True)
    loan_amount = fields.Float("Loan Amount",tracking=True)
    dd_no = fields.Integer("DD No",tracking=True)
    type_of_transaction = fields.Char("Type of Transaction",tracking=True)
    name_of_sales_manager = fields.Char("Name of Sales Manager",tracking=True)
    bt_bank_name = fields.Char("BT Bank Name",tracking=True)
    dd_deposit_name = fields.Char("DD Deposit Name",tracking=True)
    user_id = fields.Many2one("hr.employee", "User",tracking=True)
    attachment = fields.Binary("Attachment",tracking=True)
    freeze_all = fields.Boolean("Freeze All", copy=False,tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])

            if not vals.get('app_id'):
                vals['app_id'] = self.env['ir.sequence'].next_by_code('dd.deposition.seq') or _("New")
                print("seqeuce generated:::", vals['app_id'])
        return super().create(vals_list)

    _sql_constraints = [
        ('app_id_unique', 'unique(app_id)', 'App ID must be unique.'),
        ('app_id_not_null', 'CHECK(app_id IS NOT NULL)', 'App ID cannot be null.'), ]

    def action_submit(self):
        self.write({'freeze_all': True})

    def action_reset_to_draft(self):
        self.write({'freeze_all': False})
