from odoo import models, fields, api, _


class ReconcileRecords(models.Model):
    _name = 'reconcile.records'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Reconcile Records'
    _rec_name = "name"

    name = fields.Char("Label", tracking=True)
    actual_date = fields.Date("Actual Date", tracking=True)
    value_date = fields.Date("Value Date", tracking=True)
    bank_id = fields.Date("Bank", tracking=True)
    debit = fields.Float("Debit", tracking=True)
    credit = fields.Float("Credit", tracking=True)
    balance = fields.Float("Balance", tracking=True)
    app_id = fields.Char(string="App ID", readonly=True, tracking=True)

    # mis_id = fields.Many2one(comodel_name='mis.main', string="MIS")
    mis_id = fields.Many2one(comodel_name='mis.main', string="MIS")

    _sql_constraints = [
        ('uniq_name', 'unique(name)', "Label Must Be Unique"),
    ]

    def action_match(self):
        print(self.env.context.get('reco_id'))
        store = self.env.context.get('reco_id')
        print(store)
        return {
            'res_model': 'mis.main',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'view_id': self.env.ref('mis_modification.mis_main_view_tree').id,
            'target': 'new',
            'context': {'reco_id': store},
        }
