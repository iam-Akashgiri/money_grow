from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MISMain(models.Model):
    _name = 'mis.main'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'MIS'
    _rec_name = 'app_id'


    sr_no = fields.Integer("SR.NO",tracking=True)
    cpc = fields.Many2one("res.partner", "CPC",tracking=True)
    customer_name = fields.Char("Customer Name",tracking=True)
    lan_no = fields.Char("LAN No",tracking=True)
    product = fields.Char("Product - HL/LAP/ HL BT/ LAP BT",tracking=True)
    sales_manager_name = fields.Char("Sales Manager Name",tracking=True)
    sales_manager_mob_no = fields.Char("Sales Manager Mobile No",tracking=True)
    customer_contact_no = fields.Char("Customer Contact No",tracking=True)
    customer_email = fields.Char("Customer Email",tracking=True)
    loan_amount = fields.Float("Loan Amount", tracking=1)
    mode = fields.Char("Mode - Chq/DD/Online",tracking=True)
    cheq_dd = fields.Char("Cheque/DD Number",tracking=True)
    cheq_dd_amount = fields.Char("Cheque/DD Amount",tracking=True)
    clearance_date = fields.Date("Clearance Date",tracking=True)
    cheq_dd_bank_name = fields.Char("Chq/DD Bank Name",tracking=True)
    payment_details = fields.Char("Payment Details", help="Payment details as per the finacle particulars details.",tracking=True)
    vendor_payment_id = fields.Many2one("vendor.payment.confirmation", "Vendor Payment", help="Vendor Payment confirmation ( Only for vendor use )",tracking=True)
    fsd_received = fields.Char("FSD Received (Y/N)",tracking=True)
    document_sharing_status = fields.Char("Document Sharing Status",tracking=True)
    rac_remarks = fields.Many2one("rac.remarks", "RAC Remarks",tracking=True)
    vendor_remarks = fields.Many2one("vendor.remarks", "Vendor Remarks",tracking=True)
    all_data_shared_with_anulom = fields.Date("All Data Shared With Anulom",tracking=True)
    em_creation_date = fields.Date("EM Creation Date",tracking=True)
    noi_receipt_received_date = fields.Date("NOI Receipt Received Date",tracking=True)
    receipt = fields.Many2many(comodel_name='ir.attachment', string='Receipt',tracking=True)
    index_2 = fields.Many2many(comodel_name='ir.attachment',string="Index II", relation='index',tracking=True)
    customer_email_status = fields.Binary("Customer Email Status",tracking=True)
    bank_email_status = fields.Binary("Bank Email Status",tracking=True)
    submitted_to_igr = fields.Date("Submitted To IGR",tracking=True)
    token_number = fields.Integer("Token Number",tracking=True)
    sro = fields.Char("SRO",tracking=True)
    amount_receivable = fields.Float("Amount Receivable", compute='_compute_amount')
    amount_received = fields.Float("Amount Received",tracking=True)
    diff = fields.Float("Diff",tracking=True)
    rf_paid = fields.Integer("RF Paid",tracking=True)
    DHC = fields.Integer("DHC",tracking=True)
    stamp_duty = fields.Integer("Stamp Duty",tracking=True)
    comments = fields.Char("Comments",tracking=True)
    freeze_all = fields.Boolean("Freeze All", copy=False,tracking=True)
    can_edit = fields.Boolean("can_edit", copy=False, compute='_can_edit',tracking=True)
    show_submit_button = fields.Boolean("Show Submit Button", cumpute="_compute_show_submit",tracking=True)
    show_set_to_draft_button = fields.Boolean("Show Set To Draft Button", cumpute="_compute_show_set_to_draft_button",tracking=True)
    app_id = fields.Char( string='App ID',tracking=True)
    _sql_constraints = [
        ('uniq_name', 'unique(lan_no)', "Lan No Must Be Unique"),
        ('app_id_unique', 'unique(app_id)', 'App ID must be unique.'),
        ('app_id_not_null', 'CHECK(app_id IS NOT NULL)', 'App ID cannot be null.')
    ]

    def _compute_amount(self):
        for rec in self:
            rec.amount_receivable = 15000 + 2170
            if (rec.loan_amount*0.5/100) < 15000:
                rec.amount_receivable = rec.loan_amount*0.5/100 + 2170
            rec.diff = rec.amount_receivable - rec.amount_received

    def reco(self):
        print('rcooooooo')
        print(self.env.context.get('line_reco_id'))
        reco_id = self.env.context.get('line_reco_id')
        reconcilation = self.env['reconcile.records'].search([('id', '=', reco_id)])
        print(self , 'selffffffffffffff')
        if reconcilation:
            if len(self.ids) > 1:
                raise ValidationError('You can not reconcile more than 1 record at a time')
            else:
                self.amount_received = reconcilation.credit
                return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mis.main',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'current',
                'res_id': self.id
                }

    @api.depends('freeze_all')
    def _can_edit(self):
        for rec in self:
            rec.can_edit = False
            if rec.freeze_all and self.env.user.has_group('base.group_erp_manager'):
                print('entered')
                rec.can_edit = True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])

            if not vals.get('app_id'):
                vals['app_id'] = self.env['ir.sequence'].next_by_code('mis.main.seq') or _("New")
        return super().create(vals_list)


    def action_mail_to_customer(self):
        self.ensure_one()
        lang = self.env.context.get('lang')
        mail_template = self.env.ref('mis_modification.mail_template_of_attachment')
        print('mail_template....', mail_template)
        # mail_template = self._find_mail_template()
        # if mail_template and mail_template.lang:
        #     lang = mail_template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'mis.main',
            'default_res_ids': self.ids,
            'default_template_id': mail_template.id if mail_template else None,
            'default_body': mail_template.body_html if mail_template else None,
            'default_subject': mail_template.subject if mail_template else None,
            'default_send_to': self.customer_email ,
            'default_attachment_ids': [(6, 0, self.receipt.ids + self.index_2.ids)],
            # 'default_attachment_2_ids': [(6, 0, self.attachment2_ids.ids)],
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'open.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_mail_to_cpc(self):
        self.ensure_one()
        lang = self.env.context.get('lang')
        mail_template = self.env.ref('mis_modification.mail_template_of_attachment')
        print('mail_template....', mail_template)
        mail_lst = [email for email in [self.cpc.email, self.cpc.email_2, self.cpc.email_3] if email]
        comma_sep_mail = ','.join(mail_lst) if mail_lst else None
        ctx = {
            'default_model': 'mis.main',
            'default_res_ids': self.ids,
            'default_template_id': mail_template.id if mail_template else None,
            'default_body': mail_template.body_html if mail_template else None,
            'default_subject': mail_template.subject if mail_template else None,
            'default_send_to': comma_sep_mail ,
            'default_attachment_ids': [(6, 0, self.receipt.ids + self.index_2.ids)],
            # 'default_attachment_2_ids': [(6, 0, self.attachment2_ids.ids)],
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'open.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }



    def _compute_show_submit(self):
        for rec in self:
            if self.env.user.has_group('mis_modification.group_submit_form'):
                rec.hide_submit_button = True
            else:
                rec.hide_submit_button = False

    def _compute_show_set_to_draft_button(self):
        for rec in self:
            if self.env.user.has_group('mis_modification.group_set_to_draft_form'):
                rec.hide_set_to_draft_button = True
            else:
                rec.hide_set_to_draft_button = False

    @api.constrains('sales_manager_mob_no', 'customer_contact_no')
    def _check_phone_number(self):
        for rec in self:
            if (rec.sales_manager_mob_no and len(rec.sales_manager_mob_no) != 10) or (rec.customer_contact_no and len(rec.customer_contact_no) != 10):
                raise ValidationError(_("Contact Number Must Have 10 Digit"))


    # def action_mail_to_customer(self):
    #     return {
    #         'name': _('Mail Template'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'mail.template.wizard',
    #         'view_mode': 'form',
    #         'context': {'default_mail_to': self.customer_email},
    #         'target': 'new',
    #     }

    # def action_mail_to_cpc(self):
    #     mail_lst = [email for email in [self.cpc.email, self.cpc.email_2, self.cpc.email_3] if email]
    #     comma_sep_mail = ','.join(mail_lst) if mail_lst else None
    #     return {
    #         'name': _('Mail Template'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'mail.template.wizard',
    #         'view_mode': 'form',
    #         'context': {'default_mail_to': comma_sep_mail},
    #         'target': 'new',
    #     }

    def action_submit(self):
        self.write({'freeze_all': True})

    def action_reset_to_draft(self):
        self.write({'freeze_all': False})

    def action_reconcile(self):
        pass

    # is_editable_for_group = fields.Boolean(
    #     compute='_compute_is_editable_for_group',
    #     string='Is Editable for Group',
    # )
    #
    # def _compute_is_editable_for_group(self):
    #     return True
        # for record in self:
        #     record.is_editable_for_group = self.env.user.has_group('mis_modification.group_position_manager')















