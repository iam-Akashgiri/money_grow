from odoo import models, fields, api, _


class RACRemarks(models.Model):
    _name = 'rac.remarks'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'RAC Remarks'
    _rec_name = "name"

    name = fields.Char("Name", tracking=True)
    app_id = fields.Char(string="App ID",readonly=True,tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])

            if not vals.get('app_id'):
                vals['app_id'] = self.env['ir.sequence'].next_by_code('rac.remarks.seq') or _("New")
                print("seqeuce generated:::", vals['app_id'])

        return super().create(vals_list)

    _sql_constraints = [
        ('app_id_unique', 'unique(app_id)', 'App ID must be unique.'),
        ('app_id_not_null', 'CHECK(app_id IS NOT NULL)', 'App ID cannot be null.'), ]

