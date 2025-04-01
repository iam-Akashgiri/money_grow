from odoo import api,fields,models,_
#
# class RecoWizard(models.TransientModel):
#     _name = 'reco.wizard'
#
#     send_to = fields.Char(string='Send to:')
#     attachment_ids = fields.Many2many('ir.attachment', string='Attachment 1', relation='_attach_id')
#     attachment_2_ids = fields.Many2many('ir.attachment', string='Attachment 2')
#     sale_id = fields.Many2one('sale.order')
#     subject = fields.Char(string='Subject')
#
#     template_id = fields.Many2one(
#         'mail.template', 'Use template',
#     )
#     body = fields.Html(
#         'Contents',
#         render_engine='qweb', render_options={'post_process': True},
#         sanitize_style=True, readonly=False, store=True)

class OpenWizard(models.TransientModel):
    _name = 'open.wizard'

    send_to = fields.Char(string='Send to:')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment 1', relation='_attach_id')
    attachment_2_ids = fields.Many2many('ir.attachment', string='Attachment 2')
    sale_id = fields.Many2one('sale.order')
    subject = fields.Char(string='Subject')

    template_id = fields.Many2one(
        'mail.template', 'Use template',
    )
    body = fields.Html(
        'Contents',
        render_engine='qweb', render_options={'post_process': True},
        sanitize_style=True, readonly=False, store=True)

    def action_send_email(self):

        # mail_pool = self.env['mail.mail']
        # values = {}
        # values.update({'subject': 'Your Subject'})
        # values.update({'email_to': self.mail_to})
        # values.update({'body_html': '<html><body>Your Email Body</body></html>'})
        # values.update({'author_id': self.env.user.partner_id.id})
        # mail_id = mail_pool.create(values)
        # mail_id.send()


        for rec in self:
            mail_template = self.env.ref('mis_modification.mail_template_of_attachment')
            mail_template.send_mail(self.id, force_send=True)
            # rec.status = 'pending'
            # rec.message_post(body=f"Record has been share for Approval.")

