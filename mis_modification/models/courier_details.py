from odoo import models, fields, api, _


class CourierDetails(models.Model):
    _name = 'courier.details'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Courier Details'
    _rec_name = 'app_id'


    sr_no = fields.Integer("SR.NO",tracking=True)
    app_id = fields.Char(string="App ID",readonly=True,tracking=True)
    courier_company_name = fields.Many2one("res.partner", "Courier Company Name",tracking=True)
    courier_to = fields.Char("Courier To",tracking=True)
    name_of_person = fields.Char("Name of Person",tracking=True)
    address = fields.Char("Address",tracking=True)
    mob_no = fields.Char("Mob No",tracking=True)
    docket_details = fields.Char("Docket Details",tracking=True)
    particulars = fields.Char("Particulars",tracking=True)
    remarks = fields.Char("Remarks",tracking=True)
    freeze_all = fields.Boolean("Freeze All", copy=False,tracking=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])

            if not vals.get('app_id'):
                vals['app_id'] = self.env['ir.sequence'].next_by_code('courier.details.seq') or _("New")
                print("seqeuce generated:::", vals['app_id'])
        return super().create(vals_list)

    _sql_constraints = [
        ('app_id_unique', 'unique(app_id)', 'App ID must be unique.'),
        ('app_id_not_null', 'CHECK(app_id IS NOT NULL)', 'App ID cannot be null.'), ]

    def action_submit(self):
        self.write({'freeze_all': True})

    def action_reset_to_draft(self):
        self.write({'freeze_all': False})