from odoo import models, fields, api, _


class MailTemplateWizard(models.TransientModel):
    _name = 'mail.template.wizard'

    mail_template_id = fields.Many2one("mail.template", "Template")
    mail_to = fields.Char("Mail To")

    def action_send(self):
        mail_pool = self.env['mail.mail']
        values = {}
        values.update({'subject': 'Your Subject'})
        values.update({'email_to': self.mail_to})
        values.update({'body_html': '<html><body>Your Email Body</body></html>'})
        values.update({'author_id': self.env.user.partner_id.id})
        mail_id = mail_pool.create(values)
        mail_id.send()